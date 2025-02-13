"""REST API for Index."""
import hashlib
import flask
import insta485


def error(msg, status_code):
    """Return error."""
    error_context = flask.jsonify({"message": msg, "status_code": status_code})
    error_context.status_code = status_code
    return error_context


def check_authorization():
    """Check if the user is logged in."""
    auth = flask.request.authorization
    cookie_set = "username" in flask.session
    if not auth and not cookie_set:
        return flask.abort(403)
    if cookie_set:
        return flask.session["username"]
    username = auth["username"]
    password = auth["password"]
    # Finds stored password w username
    connection = insta485.model.get_db()
    stored = connection.execute(
        "SELECT password FROM users WHERE username = ?", (username,)
    ).fetchone()['password']
    if not stored:
        return flask.abort(403)
    # Checks if password matches
    algorithm, salt, hash_obj = stored.split('$')
    hash_obj2 = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj2.update(password_salted.encode('utf-8'))
    password_hash = hash_obj2.hexdigest()
    if password_hash != hash_obj:
        return flask.abort(403)
    return username


@insta485.app.route('/api/v1/')
def index():
    """Return API documentation."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": flask.request.path,
    }
    return flask.jsonify(**context)

# @insta485.app.route('/api/v1/suggested/', methods=['GET'])
# def get_suggested():
#     logname = check_authorization()
#     connection = insta485.model.get_db()
#     cur = connection.execute(
#         "SELECT username, filename "
#         "FROM users "
#         "WHERE username NOT IN (SELECT username2 "
#         "FROM following WHERE username1 == ?) "
#         "AND username != ? ",
#         (logname, logname)
#     )
#     not_following_users = cur.fetchall()
#     context = {}
#     for user in not_following_users:
#         context[user['username']] = user['filename']

#     return flask.jsonify(**context) 

# @insta485.app.route('/api/v1/follow/<username2>', methods=['POST'])
# def post_follow(username2):
#     logname = check_authorization()
#     connection = insta485.model.get_db()
#     connection.execute(
#         "INSERT INTO following (username1, username2) "
#         "VALUES (?, ?) ",
#         (logname, username2, )
#     )
#     context = {}
#     return flask.jsonify(**context)

    
# @insta485.app.route('/api/v1/posts/', methods=['GET'])
# def get_newest_posts():
#     """Return 10 newest posts."""
#     logname = check_authorization()
#     postid_lte_n = flask.request.args.get("postid_lte", default=None, type=int)
#     size = flask.request.args.get("size", default=None, type=int)
#     page = flask.request.args.get("page", default=None, type=int)
#     owner = flask.request.args.get("owner", default=None, type=str)
#     connection = insta485.model.get_db()
#     next_url = ""
#     results = []
#     path = flask.request.path
#     cur = connection.execute(
#         "SELECT postid, filename, owner, created "
#         "FROM posts "
#         "WHERE owner IN (SELECT username2 FROM following WHERE username1 == ?)"
#         "OR owner = ?",
#         (logname, logname)
#     )
#     posts = cur.fetchall()
#     posts = sorted(posts, key=lambda k: k['postid'], reverse=True)
#     next_postid_lte = posts[0]['postid']
#     if postid_lte_n:
#         next_postid_lte = postid_lte_n
#     next_page = 1 if page is None else page + 1
#     if postid_lte_n:
#         path += "?postid_lte=" + str(postid_lte_n)
#         posts = get_posts_lte(posts, postid_lte_n)
#     if size:
#         path += "?size=" + str(size)
#     if page:
#         path += "?page=" + str(page)
#     if owner:
#         path+= "?owner=" + str(owner)

#     if (page is not None and page < 0) or (size is not None and size < 0):
#         return error("Bad Request", 400)
#     posts = get_nth_page(posts, page, size)
#     for post in posts:
#         post_dict = {}
#         post_dict["postid"] = post['postid']
#         post_dict["url"] = f"/api/v1/posts/{post['postid']}/"
#         post_dict["owner"] = post['owner']
#         results.append(post_dict)
#     size = 10 if size is None else size

#     if len(posts) == size:
#         next_url = (
#             f"/api/v1/posts/?size={size}&page={next_page}"
#             f"&postid_lte={next_postid_lte}"
#         )
#     path = flask.request.full_path
#     if flask.request.full_path[-1] == "?":
#         path = path[:-1]

#     if owner:
#         results = [x for x in results if x['owner'] == owner]
#     print(len(results))
#     print(owner)
#     context = {"next": next_url, "results": results, "url": path}
#     return flask.jsonify(**context)


# def get_posts_lte(posts, num):
#     """Return post urls and ids no newer than post id N."""
#     splice_idx = len(posts)
#     for i, post in enumerate(posts):
#         if post['postid'] <= num:
#             splice_idx = i
#             break
#     if splice_idx == len(posts):
#         posts = []
#     else:
#         posts = posts[splice_idx:]
#     return posts


# def get_nth_page(posts, page, size):
#     """Return N’th page of post urls and ids."""
#     if page is None:
#         page = 0
#     if size is None:
#         size = 10
#     start_idx = min(size*page, len(posts))
#     end_idx = min(start_idx+size, len(posts))
#     size_idx = end_idx - start_idx
#     if size_idx == 0:
#         posts = []
#     else:
#         posts = posts[start_idx:end_idx]
#     # print(posts)
#     return posts


# @insta485.app.route('/api/v1/posts/<int:postid>/')
# def get_post(postid):
#     """Return post information."""
#     logname = check_authorization()
#     comment_list = []
#     likes = {}

#     connection = insta485.model.get_db()

#     post = connection.execute(
#         "SELECT created, filename, caption, owner  "
#         "FROM posts "
#         "WHERE postid = ? ",
#         (postid,)
#     )
#     post = post.fetchall()
#     if len(post) == 0:
#         return error("Not Found", 404)
#     post = post[0]
    
#     caption = post['caption']
#     logname_like_curr = connection.execute(
#             "SELECT COUNT(*), likeid "
#             "FROM likes "
#             "WHERE owner == ? "
#             "AND postid == ? ",
#             (logname, postid)
#         )
#     logname_like_curr = logname_like_curr.fetchone()
#     logname_likes_this = logname_like_curr['COUNT(*)'] > 0

#     curr_likes = connection.execute(
#             "SELECT COUNT(*) "
#             "FROM likes "
#             "WHERE postid == ? ",
#             (postid,)
#         )
#     curr_likes = curr_likes.fetchone()
#     num_likes = curr_likes['COUNT(*)']
#     if logname_likes_this:
#         likeid = f"/api/v1/likes/{logname_like_curr['likeid']}/"
#     else:
#         likeid = None
#     likes["lognameLikesThis"] = logname_likes_this
#     likes["numLikes"] = num_likes
#     likes["url"] = likeid

#     owner_img_url = connection.execute(
#         "SELECT filename "
#         "FROM users "
#         "WHERE username = ? ",
#         (post["owner"],)
#     )
#     owner_img_url = owner_img_url.fetchone()['filename']

#     owner_img_url = f"/uploads/{owner_img_url}"

#     cur = connection.execute(
#         "SELECT * "
#         "FROM comments "
#         "WHERE postid = ?",
#         (postid,)
#     )

#     for comment in sorted(cur.fetchall(),
#                           key=lambda k: k['postid'], reverse=True):
#         comment_list.append({
#             "commentid": comment["commentid"],
#             "lognameOwnsThis": logname == comment["owner"],
#             "owner": comment["owner"],
#             "ownerShowUrl": f"/users/{comment['owner']}/",
#             "text": comment["text"],
#             "url": f"/api/v1/comments/{comment['commentid']}/"
#         })

#     context = {
#         "caption": caption,
#         "comments": comment_list,
#         "comments_url": f"/api/v1/comments/?postid={postid}",
#         "created": post["created"],
#         "imgUrl": f"/uploads/{post['filename']}",
#         "likes": likes,
#         "owner": post["owner"],
#         "ownerImgUrl": owner_img_url,
#         "ownerShowUrl": f"/users/{post['owner']}/",
#         "postShowUrl": f"/posts/{postid}/",
#         "postid": postid,
#         "url": f"/api/v1/posts/{postid}/"
#     }

#     return flask.jsonify(**context)


# @insta485.app.route('/api/v1/comments/', methods=['POST', 'DELETE'])
# def add_comment():
#     """Add or delete a comment to a post."""
#     logname = check_authorization()
#     context = {}
#     status_code = 200
#     postid = flask.request.args.get("postid", default=None, type=int)
#     text = flask.request.json['text']
#     context, status_code = add_comment_helper(logname, postid, text)
#     if status_code == 404:
#         return error("Not found", 404)

#     return flask.jsonify(**context), status_code


# @insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
# def delete_comment(commentid):
#     """Delete one comment for a post."""
#     logname = check_authorization()
#     connection = insta485.model.get_db()
#     # check if commentid exists
#     cur = connection.execute(
#         "SELECT * FROM comments WHERE commentid = ?",
#         (commentid,)
#     )
#     comment = cur.fetchone()
#     if not comment:
#         return error("Not found", 404)
#     # check if logname is owner of comment
#     if logname != comment['owner']:
#         return error("Forbidden", 403)
#     connection.execute(
#         "DELETE FROM comments WHERE commentid = ?",
#         (commentid,)
#     )
#     return {}, 204


# def add_comment_helper(logname, postid, text):
#     """Add one comment to a post."""
#     # check of postid exusts
#     connection = insta485.model.get_db()
#     cur = connection.execute(
#         "SELECT * FROM posts WHERE postid = ?",
#         (postid,)
#     )
#     post = cur.fetchone()
#     if not post:
#         return None, 404
#     # add comment
#     comment = connection.execute(
#         "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
#         (logname, postid, text)
#     ).lastrowid
#     return {
#         "commentid": comment,
#         "lognameOwnsThis": True,
#         "owner": logname,
#         "ownerShowUrl": f"/users/{logname}/",
#         "text": text,
#         "url": flask.request.path + str(comment) + "/",
#     }, 201


# @insta485.app.route('/api/v1/likes/', methods=['POST'])
# def post_likes():
#     """Manage like functionality."""
#     postid = flask.request.args.get("postid", default=None, type=int)
#     logname = check_authorization()
#     context = {}
#     status_code = 200
#     context, status_code = post_helper(logname, postid)
#     if status_code == 404:
#         return error("Not found", 404)
#     return flask.jsonify(**context), status_code


# def post_helper(logname, postid):
#     """Add one “like” for a specific post."""
#     connection = insta485.model.get_db()
#     # returns error if postid not found
#     cur = connection.execute(
#         "SELECT postid FROM posts WHERE postid = ?",
#         (postid,)
#     )
#     post = cur.fetchone()
#     if not post:
#         return None, 404
#     # check if logname alr liked postid
#     cur = connection.execute(
#         "SELECT likeid FROM likes where owner = ? AND postid = ?",
#         (logname, postid)
#     )
#     like = cur.fetchone()
#     if like:
#         return {
#             "url": flask.request.path + f"{like['likeid']}/",
#             "likeid": like["likeid"],
#         }, 200
#     # if not, add like, return likeid
#     # .lastrowid works cus likeid is autoincremented and primary key
#     like = connection.execute(
#         "INSERT INTO likes (owner, postid) VALUES (?, ?)",
#         (logname, postid)
#     ).lastrowid

#     return {
#         "url": flask.request.path + f"{like}/",
#         "likeid": like,
#     }, 201


# @insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
# def delete_likes(likeid):
#     """Delete one “like” for a specific post."""
#     # checks if likeid exists
#     context = {}
#     logname = check_authorization()
#     connection = insta485.model.get_db()
#     cur = connection.execute(
#         "SELECT likeid FROM likes WHERE likeid = ?",
#         (likeid,)
#     )
#     like = cur.fetchone()
#     if not like:
#         return error("Not found", 404)
#     # checks if user is owner of likeid
#     cur = connection.execute(
#         "SELECT owner FROM likes WHERE likeid = ?",
#         (likeid,)
#     )
#     owner = cur.fetchone()
#     if owner["owner"] != logname:
#         return error("Forbidden", 403)
#     # deletes likeid
#     connection.execute(
#         "DELETE FROM likes WHERE likeid = ?",
#         (likeid,)
#     )
#     return flask.jsonify(**context), 204
