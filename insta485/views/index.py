"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import url_for
import arrow
import insta485

# START NEW STUFF
# @insta485.app.route('/waiting/')
# def show_waiting():
#     amount = flask.request.form['amount']
#     return flask.render_template("waiting.html", amount)






# END NEW STUFF





def check_login():
    """Check if user is logged in."""
    test_login = 'username' not in flask.session
    if test_login:
        return flask.redirect(flask.url_for('show_accounts', url='login'))
    return False


@insta485.app.route('/')
def show_index():
    if check_login():
        return check_login()
    connection = insta485.model.get_db()

    row = connection.execute(
        "INSERT INTO transactions (status) VALUES (?) ",
        ("created", )
    )
    transaction_id = row.lastrowid

    context = {'transaction_id': transaction_id}
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>')
def get_image(filename):
    """Serve image from uploads folder."""
    logged_in = 'username' in flask.session
    if not logged_in:
        return flask.abort(403)
    # If file doesn't exist, return 404
    try:
        return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                         filename)
    except FileNotFoundError:
        return flask.abort(404)

@insta485.app.route('/assets/<filename>')
def get_asset(filename):
    """Serve image from uploads folder."""
    logged_in = 'username' in flask.session
    # if not logged_in:
    #     return flask.abort(403)
    # If file doesn't exist, return 404
    try:
        return flask.send_from_directory(insta485.app.config['ASSET_FOLDER'],
                                         filename)
    except FileNotFoundError:
        return flask.abort(404)

# @insta485.app.route('/assets/<filename>')
# def get_asset_not_logged_in(filename):
#     """Serve image from uploads folder."""
#     # If file doesn't exist, return 404
#     try:
#         return flask.send_from_directory(insta485.app.config['ASSET_FOLDER'],
#                                          filename)
#     except FileNotFoundError:
#         return flask.abort(404)
    
@insta485.app.route('/posts/<postid_url>/')
def show_posts(postid_url):
    """Display / route."""
    if check_login():
        return check_login()
    logname = flask.session['username']

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT owner "
        "FROM posts "
        "WHERE postid = ? ",
        (postid_url, )
    )
    owner = cur.fetchone()['owner']

    cur = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "WHERE postid == ? ",
        (postid_url, )
    )

    post = cur.fetchall()
    post = post[0]

    post['created'] = arrow.get(post['created']).humanize()
    cur3 = connection.execute(
        "SELECT COUNT(*)"
        "FROM likes "
        "WHERE postid == ?",
        (post['postid'], )
    )
    cur4 = connection.execute(
        "SELECT *"
        "FROM comments "
        "WHERE postid == ?",
        (post['postid'], )
    )
    cur5 = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username == ? ",
        (post['owner'], )
    )
    cur6 = connection.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=? AND owner=? ",
        (post['postid'], logname)
    )

    cur7 = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username == ? ",
        (logname, )
    )

    post['likes'] = cur3.fetchone()['COUNT(*)']
    post['comments'] = sorted(cur4.fetchall(), key=lambda k: k['commentid'])
    post['ownerpfp'] = cur5.fetchone()['filename']
    post['liked'] = cur6.fetchone()['COUNT(*)'] > 0
    post['logname'] = logname
    post['owner'] = owner
    post['page'] = "none"
    post['pfp'] = cur7.fetchone()['filename']
    return flask.render_template("posts.html", **post)


@insta485.app.route('/users/<user_url>/')
def show_user(user_url):
    """Display /users/<user_url> route."""
    if check_login():
        return check_login()
    connection = insta485.model.get_db()
    logname = flask.session['username']
    cur7 = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username == ? ",
            (logname, )
        )

    pfp = cur7.fetchone()['filename']

    cur7 = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username == ? ",
            (user_url, )
        )

    user_pfp = cur7.fetchone()['filename']
    
    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username == ?",
        (user_url, )
    )
    users = cur.fetchall()
    if connection.execute(
        "SELECT COUNT(*) "
        "FROM users "
        "WHERE username == ?",
        (user_url, )
    ).fetchone()['COUNT(*)'] == 0:
        return flask.abort(404)
    # Connect to database
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner == ?",
        (user_url, )
    )
    posts = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM following "
        "WHERE username1 == ? "
        "AND username2 == ? ",
        (logname, user_url)
    )
    relationship = cur.fetchone()['COUNT(*)']

    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM following "
        "WHERE username2 == ? ",
        (user_url, )
    )
    followers = cur.fetchone()['COUNT(*)']

    cur5 = connection.execute(
        "SELECT COUNT(*) "
        "FROM following "
        "WHERE username1 == ? ",
        (user_url, )
    )
    following = cur5.fetchone()['COUNT(*)']

    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM posts "
        "WHERE owner == ? ",
        (user_url, )
    )
    num_posts = cur.fetchone()['COUNT(*)']

    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ? ",
        (logname, )
    )
    following_usernames = cur.fetchall()
    following_usernames = [i['username2'] for i in following_usernames]
    followed_by = []
    for username in following_usernames:
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (username, user_url, )
        )
        followed_by_cur = [i['username1'] for i in cur.fetchall()]
        followed_by.extend(followed_by_cur)
    followed_by_1 = ""
    followed_by_2 = ""
    followed_by_3 = ""
    if len(followed_by) >= 1:
        followed_by_1 = followed_by[0]
    if len(followed_by) >= 2:
        followed_by_2 = ", "+followed_by[1]
    if len(followed_by) >= 3:
        followed_by_3 = ", "+followed_by[2]

    followed_by_more = ""
    if len(followed_by) > 3:
        followed_by_more = f"+ {len(followed_by)-3} more"

    cur = connection.execute(
        "SELECT bio "
        "FROM users "
        "WHERE username = ? ",
        (user_url, )
    )
    bio = cur.fetchone()['bio']
    
    likes = {}
    comments = {}
    for post in posts:
        cur3 = connection.execute(
            "SELECT COUNT(*) "
            "FROM likes "
            "WHERE postid = ? ",
            (post['postid'], )
        )
        like_count = cur3.fetchone()['COUNT(*)']
        likes[post['postid']] = like_count

        cur4 = connection.execute(
            "SELECT COUNT(*) "
            "FROM comments "
            "WHERE postid = ? ",
            (post['postid'], )
        )
        
        comment_count = cur4.fetchone()['COUNT(*)']
        comments[post['postid']] = comment_count

    is_user = logname == user_url
    print("||||")
    print(posts)
    context = {"logname": logname, "page": "profile", "pfp": pfp, "user_pfp": user_pfp, "users": users, "posts": posts,
               "is_user": is_user, "relationship": relationship,
               "followers": followers, "following": following, "bio": bio,
               "num_posts": num_posts, "followed_by_1": followed_by_1, "followed_by_2": followed_by_2, "followed_by_3": followed_by_3, "followed_by_more": followed_by_more, "likes": likes, "comments": comments}

    if is_user:
        context["relationship"] = ""
    elif relationship == 1:
        context["relationship"] = "following"
    else:
        context["relationship"] = "not following"

    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<user_url>/<action>/')
def show_follow(user_url, action):
    """Display /users/<user_url>/<action> route."""
    if check_login():
        return check_login()
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == ?",
        (user_url, )
    )
    test_abort = connection.execute(
        "SELECT COUNT(*) "
        "FROM users "
        "WHERE username = ?",
        (user_url, )
    )
    if test_abort.fetchone()['COUNT(*)'] == 0:
        return flask.abort(404)
    follow_list = []
    if action == "following":
        cur = connection.execute(
            "SELECT username, filename "
            "FROM users "
            "WHERE username IN (SELECT username2 "
            "FROM following WHERE username1 == ?)",
            (user_url, )
        )
        follow_list = cur.fetchall()
    elif action == "followers":
        cur = connection.execute(
            "SELECT username, filename "
            "FROM users "
            "WHERE username IN (SELECT username1 "
            "FROM following WHERE username2 == ?)",
            (user_url, )
        )
        follow_list = cur.fetchall()
    for user in follow_list:
        cur = connection.execute(
            "SELECT COUNT(*) "
            "FROM following "
            "WHERE username1 == ? "
            "AND username2 == ? ",
            (logname, user['username'])
        )
        user['follows'] = cur.fetchone()['COUNT(*)'] > 0
    context = {"logname": logname, "page": "none", "follow_list": follow_list,
               "action": action, "looking_at": user_url}
    return flask.render_template("follow.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if check_login():
        return check_login()
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur7 = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username == ? ",
        (logname, )
    )

    pfp = cur7.fetchone()['filename']
    
    # select all users that logname does NOT follow
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username NOT IN (SELECT username2 "
        "FROM following WHERE username1 == ?) "
        "AND username != ? ",
        (logname, logname)
    )
    rows = cur.fetchall()
    not_following = [row['username'] for row in rows]
    not_following_posts = []
    for name in not_following:
        cur2 = connection.execute(
            "SELECT postid, filename "
            "FROM posts "
            "WHERE owner == ? ",
            (name, )
        )
        not_following_posts.extend(cur2.fetchall())

    likes = {}
    comments = {}
    for post in not_following_posts:
        cur3 = connection.execute(
            "SELECT COUNT(*) "
            "FROM likes "
            "WHERE postid = ? ",
            (post['postid'], )
        )
        like_count = cur3.fetchone()['COUNT(*)']
        likes[post['postid']] = like_count

        cur4 = connection.execute(
            "SELECT COUNT(*) "
            "FROM comments "
            "WHERE postid = ? ",
            (post['postid'], )
        )
        
        comment_count = cur4.fetchone()['COUNT(*)']
        comments[post['postid']] = comment_count

    cur5 = connection.execute(
        "SELECT fullname, username, filename "
        "FROM users "
        "WHERE username NOT IN (SELECT username2 "
        "FROM following WHERE username1 == ?) "
        "AND username != ? ",
        (logname, logname)
    )
    not_following_users = cur5.fetchall()
    context = {"logname": logname, "pfp":pfp, "page": "explore", "posts": not_following_posts, "not_following": rows, "likes": likes, "comments": comments, "not_following_users": not_following_users}
    return flask.render_template("explore.html", **context)


@insta485.app.route('/create/upload')
def show_create_post():
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur7 = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username == ? ",
        (logname, )
    )

    pfp = cur7.fetchone()['filename']
    context = {"logname": logname, "pfp": pfp}
    return flask.render_template("create_post.html", **context)


@insta485.app.route('/create/post/<filename>/')
def show_create_post2(filename):
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur7 = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username == ? ",
        (logname, )
    )

    pfp = cur7.fetchone()['filename']
    context = {"logname": logname, "pfp": pfp, "filename": filename}
    return flask.render_template("create_post2.html", **context)



@insta485.app.route('/accounts/<url>/', methods=['POST', 'GET'])
def show_accounts(url):
    """Display /accounts/<url> route."""
    link_dict = {
        "login": login,
        "create": create,
        "delete": delete,
        "edit": edit,
        "password": password,
        "auth": auth
    }

    if url in link_dict:
        return link_dict[url]()
    return None


def login():
    """Display /accounts/login route."""
    logged_in = 'username' in flask.session
    if logged_in:
        return flask.redirect(url_for('show_index'))
    return flask.render_template("login.html")


def create():
    """Display /accounts/create route."""
    logged_in = 'username' in flask.session
    if logged_in:
        return flask.redirect(url_for('show_acconuts', url='edit'))
    return flask.render_template("create.html")


def delete():
    """Display /accounts/delete route."""
    logged_in = 'username' in flask.session
    if not logged_in:
        return flask.abort(403)
    logname_dict = {"logname": flask.session['username']}
    return flask.render_template("delete.html", **logname_dict)


def edit():
    """Display /accounts/edit route."""
    logged_in = 'username' in flask.session
    if not logged_in:
        return flask.abort(403)
    connection = insta485.model.get_db()
    curr = connection.execute(
        "SELECT filename, fullname, email, username, bio "
        "FROM users "
        "WHERE username == ? ",
        (flask.session['username'], )
    )
    user = curr.fetchone()
    logname_dict = {"logname": flask.session['username']}
    return flask.render_template("edit.html", user=user, **logname_dict)


def auth():
    """Display /accounts/auth route."""
    logged_in = 'username' in flask.session
    if logged_in:
        return flask.Response(status=200)
    return flask.abort(403)


def password():
    """Display /accounts/password route."""
    logged_in = 'username' in flask.session
    if not logged_in:
        return flask.abort(403)
    logname_dict = {"logname": flask.session['username']}
    return flask.render_template("password.html", **logname_dict)
