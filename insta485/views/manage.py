"""Insta485 manage function for files."""
import os
import hashlib
import pathlib
import uuid
import flask
from flask import url_for
import insta485
import yagmail
import stripe

def check_login():
    """Check if user is logged in."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_accounts', url='login'))
    return False

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def charge_buyer(amount):
    amount = amount*100  # Convert to cents
    payment_method_id = ["card"]  # Payment token from frontend

    try:
        # Create a PaymentIntent to hold the funds in escrow
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method=payment_method_id,
            confirmation_method="manual",
            confirm=True,
            capture_method="manual"  # This holds the payment without capturing
        )

        return flask.jsonify({"status": "success", "transaction_id": payment_intent.id}), 200

    except stripe.error.StripeError as e:
        return flask.jsonify({"status": "failed", "error": str(e)}), 400

def approve_payment(transaction_id, amount):
    data = flask.request.json
    seller_stripe_account = data["seller_stripe_account"]
    amount = amount * 100  # Convert to cents

    try:
        # Capture the payment (release funds to middleman)
        stripe.PaymentIntent.capture(transaction_id)

        # Transfer funds from middleman to seller
        transfer = stripe.Transfer.create(
            amount=amount,
            currency="usd",
            destination=seller_stripe_account
        )

        return flask.jsonify({"status": "success", "transfer_id": transfer.id}), 200

    except stripe.error.StripeError as e:
        return flask.jsonify({"status": "failed", "error": str(e)}), 400

def reject_payment(transaction_id):
    try:
        # Refund the buyer
        stripe.Refund.create(payment_intent=transaction_id)

        return flask.jsonify({"status": "success", "refund_id": transaction_id}), 200

    except stripe.error.StripeError as e:
        return flask.jsonify({"status": "failed", "error": str(e)}), 400


@insta485.app.route('/wait/<transaction_id>', methods=["POST"])
def manage_wait(transaction_id):
    # target = flask.request.args.get('target')
    if check_login():
        return check_login()
    logname = flask.session['username']
    connection = insta485.model.get_db()
    amount = flask.request.form['amount']
    receiver = flask.request.form['receiver']
    charge_buyer(amount)

    status = connection.execute(
        "SELECT status "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone()['status']

    context = {'amount': amount, 'transaction_id': transaction_id, 'status': status}

    if status == "created":
        connection.execute(
            "UPDATE transactions "
            "SET sender_username = ?, receiver_username = ?, amount = ?, status = ? "
            "WHERE transaction_id = ?",
            (logname, receiver, amount, "waiting", transaction_id, )
        )

        # send email
        receiver_email = connection.execute(
            "SELECT email "
            "FROM users "
            "WHERE username = ?",
            (receiver,)
        ).fetchone()['email']

        yag = yagmail.SMTP("sanjivp2703@gmail.com", "aiyv zsyl xaea vnre")
        html_content = f"""
        
    <html>
        <p> Approve receiving ${amount} </p>
        <p>Transaction ID: {transaction_id}</p>
        <form action="{ url_for('manage_verdict', transaction_id = transaction_id, status = 'approved', _external=True) }" method="post" enctype="multipart/form-data">
            <input type="submit" name = "approve_status" value="I Approve" />
        </form>
        <form action="{ url_for('manage_verdict', transaction_id = transaction_id, status = 'rejected', _external=True) }" method="post" enctype="multipart/form-data">
            <input type="submit" name = "approve_status" value="I Reject" />
        </form>
    </html>
    """
        yag.send(
        to=receiver_email,
        subject="THIS IS FOR A CODING PROJECT - SANJIV",
        contents=html_content
        )

        context['status'] = 'waiting'
    
    return flask.render_template("waiting.html", **context)


@insta485.app.route('/verdict/<transaction_id>/<status>', methods=["POST"])
def manage_verdict(transaction_id, status):
    #UPDATE DATABASE
    connection = insta485.model.get_db()

    connection.execute(
        "UPDATE transactions "
        "SET status = ? "
        "WHERE transaction_id = ? ",
        ("Payment Processing", transaction_id, )

    )
    if status == "approved":
        approve_payment(transaction_id, amount)
    elif status == "rejected":
        reject_payment(transaction_id)
    else:
        flask.abort(400)
    connection.execute(
        "UPDATE transactions "
        "SET status = ? "
        "WHERE transaction_id = ? ",
        (status, transaction_id, )

    )

    #SEND MONEY
    #SET CONTEXT
    amount = connection.execute(
        "SELECT amount "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone()['amount']


    context = {'amount': amount, 'transaction_id': transaction_id, 'status': status}
    return flask.render_template("verdict.html", **context)


# @insta485.app.route('/following/', methods=["POST"])
# def manage_follow():
#     """Manage following."""
#     if 'username' not in flask.session:
#         return check_login()
#     logname = flask.session['username']
#     target = flask.request.args.get('target')
#     if target is None:
#         target = "/"

#     connection = insta485.model.get_db()
#     acted_on = flask.request.form['username']
#     operation = flask.request.form['operation']
#     curr = connection.execute(
#         "SELECT COUNT(*) "
#         "FROM following "
#         "WHERE username1 == ? "
#         "AND username2 == ? ",
#         (logname, acted_on)
#     )
#     followed = curr.fetchone()['COUNT(*)'] > 0
#     if operation == "follow":
#         if followed:
#             return flask.abort(409)
#         connection.execute(
#             "INSERT INTO following "
#             "(username1, username2) VALUES (?, ?) ",
#             (logname, acted_on)
#         )
#     else:
#         if not followed:
#             return flask.abort(409)
#         connection.execute(
#             "DELETE FROM following "
#             "WHERE username1=? AND username2=? ",
#             (logname, acted_on)
#         )
#     return flask.redirect(target)


# @insta485.app.route('/likes/', methods=["POST"])
# def manage_likes():
#     """Manage likes."""
#     if check_login():
#         return check_login()
#     logname = flask.session['username']
#     connection = insta485.model.get_db()
#     operation = flask.request.form['operation']
#     postid = flask.request.form['postid']
#     target = flask.request.args.get('target')
#     if target is None:
#         target = "/"

#     if operation == 'like':
#         curr = connection.execute(
#             "SELECT COUNT(*) "
#             "FROM likes "
#             "WHERE owner == ? "
#             "AND postid == ? ",
#             (logname, postid)
#         )
#         liked = curr.fetchone()['COUNT(*)'] > 0
#         if liked:
#             flask.abort(409)
#         connection.execute(
#             "INSERT INTO likes "
#             " (owner, postid) VALUES (?, ?) ",
#             (logname, postid)
#         )
#     elif operation == 'unlike':
#         curr = connection.execute(
#             "SELECT COUNT(*) "
#             "FROM likes "
#             "WHERE owner == ? "
#             "AND postid == ? ",
#             (logname, postid)
#         )
#         unliked = curr.fetchone()['COUNT(*)'] == 0
#         if unliked:
#             flask.abort(409)
#         connection.execute(
#             "DELETE FROM likes "
#             "WHERE owner=? AND postid=? ",
#             (logname, postid)
#         )
#     return flask.redirect(target)


# @insta485.app.route('/comments/', methods=["POST"])
# def manage_comments():
#     """Manage comments."""
#     if check_login():
#         return check_login()
#     logname = flask.session['username']
#     connection = insta485.model.get_db()
#     operation = flask.request.form['operation']
#     target = flask.request.args.get('target')
#     if target is None:
#         target = "/"

#     if operation == "create":
#         text = flask.request.form['text']
#         postid = flask.request.form['postid']
#         if text == "" or text is None:
#             return flask.abort(400)
#         connection.execute(
#             "INSERT INTO comments "
#             " (owner, postid, text) VALUES (?, ?, ?) ",
#             (logname, postid, text)
#         )
#     elif operation == "delete":
#         # error if user tries deleting comment not owned
#         commentid = flask.request.form['commentid']
#         checker = connection.execute(
#             "SELECT commentid "
#             "FROM comments "
#             "WHERE commentid == ? AND owner == ? ",
#             (commentid, logname)
#         ).fetchone()
#         if not checker:
#             return flask.abort(403)
#         connection.execute(
#             "DELETE FROM comments "
#             "WHERE commentid == ?",
#             (commentid, )
#         )
#     return flask.redirect(target)

# @insta485.app.route('/posts/', methods=["POST"])
# def manage_posts():
#     """Manage posts."""
#     if check_login():
#         return check_login()
#     logname = flask.session['username']
#     connection = insta485.model.get_db()
#     operation = flask.request.form['operation']
#     target = flask.request.args.get('target')
#     if target is None:
#         target = url_for('show_user', user_url=logname)
#     if operation == "create1":
#         fileobj = flask.request.files['file']
#         filename = fileobj.filename
#         if filename is None or filename == "":
#             return flask.abort(400)
#         stem = uuid.uuid4().hex
#         suffix = pathlib.Path(filename).suffix.lower()
#         uuid_basename = f"{stem}{suffix}"
#         path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
#         fileobj.save(path)
#         # connection.execute(
#         #     "INSERT INTO posts "
#         #     " (filename, owner) VALUES (?, ?) ",
#         #     (uuid_basename, logname)
#         # )
#         return flask.redirect(flask.url_for('show_create_post2', filename = uuid_basename))
#     elif operation == "create2":
#         filename = flask.request.form['filename']
#         caption = flask.request.form['text']
#         print(caption)
#         connection.execute(
#             "INSERT INTO posts "
#             " (filename, caption, owner) VALUES (?, ?, ?) ",
#             (filename, caption, logname)
#         )
#     elif operation == "delete":
#         # check if owner of postid == logname
#         filepath = insta485.app.config['UPLOAD_FOLDER']
#         postid = flask.request.form['postid']
#         cur = connection.execute(
#             "SELECT * "
#             "FROM posts "
#             "WHERE postid == ? AND owner == ? ",
#             (postid, logname)
#         ).fetchone()
#         if not cur:
#             return flask.abort(403)
#         os.remove(filepath/cur['filename'])
#         connection.execute(
#             "DELETE FROM posts "
#             "WHERE postid == ? ",
#             (postid, )
#         )
#     return flask.redirect(target)


# @insta485.app.route('/accounts/logout/', methods=['POST'])
# def manage_logout():
#     """Manage logout."""
#     flask.session.clear()
#     return flask.redirect(url_for('show_accounts', url='login'))


@insta485.app.route('/accounts/', methods=["POST", "GET"])
def manage_accounts():
    """Manage accounts."""
    connection = insta485.model.get_db()
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    if target is None or target == "":
        target = "/"
    if operation == "login":
        return manage_login(connection, target)
    if operation == "edit_account":
        return manage_edit(connection, target)
    if operation == "create":
        return manage_create(target, flask.request.form['username'],
                             connection)
    if operation == "delete":
        pfp_file = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username == ? ",
            (flask.session['username'], )
        ).fetchone()
        os.remove(insta485.app.config['UPLOAD_FOLDER']/pfp_file['filename'])
        post_files = connection.execute(
            "SELECT filename "
            "FROM posts "
            "WHERE owner == ? ",
            (flask.session['username'], )
        ).fetchall()
        for file in post_files:
            os.remove(insta485.app.config['UPLOAD_FOLDER']/file['filename'])
        connection.execute(
            "DELETE FROM users "
            "WHERE username = ? ",
            (flask.session['username'], )
        )
        flask.session.clear()
    if operation == "update_password":
        old_pw = flask.request.form['password']
        new_pw1 = flask.request.form['new_password1']
        new_pw2 = flask.request.form['new_password2']
        status = -1
        if not old_pw or not new_pw1 or not new_pw2:
            status = 400
        elif new_pw1 != new_pw2:
            status = 401
        if status != -1:
            return flask.abort(status)
        row = connection.execute(
            "SELECT password FROM users WHERE username == ?",
            (flask.session['username'], )).fetchone()
        if not verify_pw(row['password'], old_pw):
            return flask.abort(403)
        connection.execute(
            "UPDATE users "
            "SET password = ? "
            "WHERE username == ? ",
            (hash_password(new_pw1), flask.session['username'])
        )
    return flask.redirect(target)


def hash_password(password):
    """Hash a password for storing."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def verify_pw(stored, provided):
    """Verify a stored password against one provided by user."""
    algorithm, salt, hash_obj = stored.split('$')
    hash_obj2 = hashlib.new(algorithm)
    password_salted = salt + provided
    hash_obj2.update(password_salted.encode('utf-8'))
    password_hash = hash_obj2.hexdigest()
    return password_hash == hash_obj


def manage_create(target, username, connection):
    """Create a user."""
    fullname = flask.request.form['fullname']
    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']
    fileobj = flask.request.files['file']
    bio = flask.request.form['bio']
    filename = fileobj.filename
    if (
        username == "" or
        password == "" or
        email == "" or
        fullname == "" or
        filename == "" or
        bio == ""
    ):
        return flask.abort(400)
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    row = connection.execute(
        "SELECT * FROM users WHERE username == ?",
        (username, )
    ).fetchone()
    if row:
        flask.abort(409)
    connection.execute(
        "INSERT INTO users "
        "(username, fullname, email, filename, password, bio) "
        "Values (?, ?, ?, ?, ?, ?) ",
        (username, fullname, email, uuid_basename, hash_password(password), bio)
    )
    flask.session['username'] = username
    return flask.redirect(target)


def manage_edit(connection, target):
    """Edit a user."""
    email = flask.request.form['email']
    fullname = flask.request.form['fullname']
    fileobj = flask.request.files['file']
    bio = flask.request.form['bio']
    filename = fileobj.filename
    if email == "" or fullname == "":
        return flask.abort(400)
    if filename == "":
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, bio = ? "
            "WHERE username == ? ",
            (fullname, email, bio, flask.session['username'], )
        )
    else:
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        # Delete
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, filename = ? "
            "WHERE username == ? ",
            (fullname, email, uuid_basename, flask.session['username'])
        )
    return flask.redirect(target)


def manage_login(connection, target):
    """Login a user."""
    username = flask.request.form['username']
    password = flask.request.form['password']
    if username == "" or password == "":
        return flask.abort(400)
    curr = connection.execute(
        "SELECT password FROM users WHERE username == ?",
        (username,)
    )
    row = curr.fetchone()
    valid = False
    if row:
        valid = verify_pw(row['password'], password)
    if valid:
        flask.session['username'] = username
        return flask.redirect(target)
    return flask.abort(403)
