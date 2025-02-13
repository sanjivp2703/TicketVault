"""Views, one for each Insta485 page."""
import insta485.api  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.index import show_index
from insta485.views.index import show_user
from insta485.views.index import get_image
from insta485.views.index import check_login
# from insta485.views.index import show_posts
# from insta485.views.index import show_follow
# from insta485.views.index import show_explore
from insta485.views.index import show_accounts
# from insta485.views.manage import manage_follow
# from insta485.views.manage import manage_likes
# from insta485.views.manage import manage_comments
# from insta485.views.manage import manage_logout
# from insta485.views.manage import manage_posts
from insta485.views.manage import manage_accounts
