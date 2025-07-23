"""Insta485 manage function for files."""
import os
import hashlib
import pathlib
import uuid
import stripe
import flask
from flask import url_for
import insta485

stripe.api_key = "sk_test_51QrpdQC07BpFIQPX9s25iHN5nA78PYrurooQeTqtiEUhqBhzC8qcl3BHd6ZDFYCNLM6fGS1ynqwHY0uKtZ19zSDe00OalrifSw"


def check_login():
    """Check if user is logged in."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_accounts', url='login'))
    return False

@insta485.app.route('/initiate/<int:transaction_id>/<user_type>', methods=["POST", "GET"])
def manage_initiate_transaction(transaction_id, user_type):
    connection = insta485.model.get_db()

    logname = flask.session['username']
    if user_type == "buyer":
        payment_sent = flask.request.form['payment_sent']
        seller = flask.request.form['seller']
        ticket_description = flask.request.form['ticket_requested']
        connection.execute(
            "UPDATE transactions "
            "SET buyer_username = ?, seller_username = ?, buyer_status = ?, price = ?, ticket_description = ?"
            "WHERE transaction_id = ? ",
            (logname, seller, "payment_supplied", payment_sent, ticket_description, transaction_id, )
        )
    elif user_type == "seller":
        fileobj = flask.request.files['ticket_image']
        filename = fileobj.filename
        if filename is None or filename == "":
            return flask.abort(400)
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        ticket_description = flask.request.form['ticket_description']
        buyer = flask.request.form['buyer']
        price_requested = flask.request.form['payment_requested']
        connection.execute(
            "UPDATE transactions "
            "SET seller_username = ?, buyer_username = ?, seller_status = ?, ticket_file = ?, ticket_description = ?, price = ? "
            "WHERE transaction_id = ? ",
            (logname, buyer, "ticket_uploaded", uuid_basename, ticket_description, price_requested, transaction_id, )
        )
        return seller_onboarding()

    
    return flask.redirect(url_for('manage_transaction', transaction_id=transaction_id, user_type = user_type)) 

def check_user(transaction_id, user_type):
    logname = flask.session['username']
    connection = insta485.model.get_db()

    if user_type == "buyer":
        user = connection.execute(
            "SELECT buyer_username "
            "FROM transactions "
            "WHERE transaction_id = ? ",
            (transaction_id, )
        ).fetchone()['buyer_username']
    elif user_type == "seller":
        user = connection.execute(
            "SELECT seller_username "
            "FROM transactions "
            "WHERE transaction_id = ? ",
            (transaction_id, )
        ).fetchone()['seller_username']

    if logname != user:
        flask.abort(404)

@insta485.app.route('/transaction/<int:transaction_id>/<user_type>', methods=["GET"])
def manage_transaction(transaction_id, user_type):
    if check_login():
        return check_login()

    check_user(transaction_id, user_type)

    connection = insta485.model.get_db()

    transaction = connection.execute(
        "SELECT buyer_status, seller_status, price, ticket_file, ticket_description, expected_ticket_send_time "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone()

    context = {
        'transaction_id': transaction_id,
        'user_type': user_type,
        'buyer_status': transaction['buyer_status'],
        'seller_status': transaction['seller_status'],
        'payment': transaction['price'],
        'ticket_file': transaction['ticket_file'],
        'ticket_requested': transaction['ticket_description'],
        'expected_ticket_send_time': transaction['expected_ticket_send_time']
    }
    return flask.render_template("waiting.html", **context)



@insta485.app.route('/payment/<int:transaction_id>/<user_type>', methods=["POST"])
def manage_payment(transaction_id, user_type):
    connection = insta485.model.get_db()
    if user_type == "seller":
        fileobj = flask.request.files['ticket_image']
        filename = fileobj.filename
        if filename is None or filename == "":
            return flask.abort(400)
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        connection.execute(
            "UPDATE transactions "
            "SET ticket_file = ? "
            "WHERE transaction_id = ?",
            (uuid_basename, transaction_id)
        )
        
        connection.execute(
            "UPDATE transactions "
            "SET seller_status = ? "
            "WHERE transaction_id = ? ",
            ("ticket_uploaded", transaction_id, )
        )

    elif user_type == "buyer":
        connection.execute(
            "UPDATE transactions "
            "SET buyer_status = ? "
            "WHERE transaction_id = ? ",
            ("payment_supplied", transaction_id, )
        )

    buyer_status, seller_status = connection.execute(
        "SELECT buyer_status, seller_status "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone().values()
    if buyer_status == "payment_supplied" and seller_status == "ticket_uploaded":
        connection.execute(
            "UPDATE transactions "
            "SET buyer_status = ?, seller_status = ?"
            "WHERE transaction_id = ? ",
            ("waiting_for_approval", "waiting_for_approval", transaction_id, )
        )
    if user_type == "buyer":
        return send_payment_buyer(transaction_id)
    return flask.redirect(url_for('manage_transaction', transaction_id = transaction_id, user_type = user_type))




@insta485.app.route('/approved/<transaction_id>/<user_type>', methods=["GET", "POST"])
def manage_approved(transaction_id, user_type):
    connection = insta485.model.get_db()
    expected_ticket_send_time = connection.execute(
        "SELECT expected_ticket_send_time FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()['expected_ticket_send_time']

    context = {
        "user_type": user_type,
        "expected_ticket_send_time": expected_ticket_send_time
    }
    send_payment_seller(transaction_id)
    return flask.render_template("approved.html", **context)
 
def send_payment_buyer(transaction_id):
    connection = insta485.model.get_db()
    amount = connection.execute(
        "SELECT price "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone()['price']
    amount *= 100
    

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Transaction Payment',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url = 'http://localhost:8000/success',
        cancel_url = 'http://localhost:8000/cancel',

    )
    return flask.redirect(session.url, code=303)

def seller_onboarding():
    logname = flask.session['username']
    connection = insta485.model.get_db()
    email, firstname, lastname = connection.execute(
        "SELECT email, firstname, lastname "
        "FROM users "
        "WHERE username = ? ",
        (logname, )
    ).fetchone().values()

    account = stripe.Account.create(
        type="express",
        country="US",
        email=email,
        business_type="individual",
        capabilities={"transfers": {"requested": True}},
        individual={
            "first_name": firstname,
            "last_name": lastname,
            "email": email
        },
        business_profile={
            "product_description": "Selling event tickets on Peer-to-peer platform for ticket resales."
        }
    )

    connection.execute(
        "UPDATE users "
        "SET stripe_id = ? "
        "WHERE username = ? ",
        (account.id, logname, )
    )
    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url="http://localhost:8000/reauth",
        return_url="http://localhost:8000/onboarding_complete",
        type="account_onboarding",
    )

    return flask.redirect(account_link.url)

def send_payment_seller(transaction_id):
    connection = insta485.model.get_db()
    seller, price = connection.execute(
        "SELECT seller_username, price "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone().values()
    price *= 100
    print(price)
    stripe_id = connection.execute(
        "SELECT stripe_id "
        "FROM users "
        "WHERE username = ?",
        (seller, )
    ).fetchone()['stripe_id']

    transfer = stripe.Transfer.create(
        amount=price,
        currency="usd",
        destination=stripe_id,
        transfer_group=transaction_id
    )

@insta485.app.route('/rejected/<transaction_id>/<user_type>', methods=["GET"])
def manage_rejected(transaction_id, user_type):
    logname = flask.session['username']
    connection = insta485.model.get_db()
    buyer, buyer_status, seller, seller_status = connection.execute(
        "SELECT buyer_username, buyer_status, seller_username, seller_status "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone().values()
    rejector = buyer if buyer_status == "rejected" else seller
    print(logname)
    print(rejector)
    if rejector == logname: rejector = "Me" 
    print(rejector)
    context = {"rejector": rejector, "user_type": user_type}
    return flask.render_template("rejected.html", **context)
 


@insta485.app.route('/verdict/<transaction_id>/<user_type>/<verdict>', methods=["POST", "GET"])
def manage_verdict(transaction_id, user_type, verdict):
    #UPDATE DATABASE
    connection = insta485.model.get_db()
    if user_type == "buyer":
        connection.execute(
            "UPDATE transactions "
            "SET buyer_status = ? "
            "WHERE transaction_id == ? ",
            (verdict, transaction_id, )
        )
    elif user_type == "seller":
        connection.execute(
            "UPDATE transactions "
            "SET seller_status = ? "
            "WHERE transaction_id == ? ",
            (verdict, transaction_id, )
        )

    buyer_status, seller_status, buyer_username, seller_username = connection.execute(
        "SELECT buyer_status, seller_status, buyer_username, seller_username "
        "FROM transactions "
        "WHERE transaction_id = ? ",
        (transaction_id, )
    ).fetchone().values()

    if buyer_status == "approved" and seller_status == "approved":
        # Calculate and set expected send time
        from datetime import datetime, timedelta
        expected_time = datetime.now() + timedelta(days=1)
        connection.execute(
            "UPDATE transactions "
            "SET expected_ticket_send_time = ? "
            "WHERE transaction_id = ?",
            (expected_time, transaction_id)
        )
        return flask.redirect(url_for('manage_approved', transaction_id = transaction_id, user_type = user_type))
    
    if buyer_status == "rejected" or seller_status == "rejected":
        return flask.redirect(url_for('manage_rejected', transaction_id = transaction_id, user_type=user_type))
    else:
        return flask.redirect(url_for('manage_transaction', transaction_id=transaction_id, user_type = user_type)) 


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

@insta485.app.route('/accounts/logout/', methods=['POST'])
def manage_logout():
    """Manage logout."""
    flask.session.clear()
    return flask.redirect(url_for('show_accounts', url='login'))

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
