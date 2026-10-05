"""Authentication and access-control behaviour."""

from conftest import ADMIN_EMAIL, SELLER_EMAIL

from insta485.views.manage import hash_password, verify_pw


def test_anonymous_user_is_redirected_to_sign_in(client):
    for path in ("/", "/index", "/seller", "/withdraw"):
        response = client.get(path)
        assert response.status_code == 302, path
        assert response.headers["Location"].endswith("/accounts/login/"), path


def test_home_routes_seller_and_admin_to_their_dashboards(seller_client, app):
    assert seller_client.get("/").headers["Location"].endswith("/index")

    with app.test_client() as admin:
        with admin.session_transaction() as session:
            session["email"] = ADMIN_EMAIL
        assert admin.get("/").headers["Location"].endswith("/admin")


def test_admin_dashboard_requires_admin(client, seller_client):
    assert client.get("/admin").status_code == 403
    assert seller_client.get("/admin").status_code == 403


def test_admin_dashboard_renders_for_admin(admin_client):
    assert admin_client.get("/admin").status_code == 200


def test_password_hash_round_trip():
    stored = hash_password("correct horse battery staple")
    assert stored != "correct horse battery staple"
    assert verify_pw(stored, "correct horse battery staple")
    assert not verify_pw(stored, "wrong password")


def test_sign_in_with_valid_credentials(client, app):
    import sqlite3

    connection = sqlite3.connect(app.config["DATABASE_FILENAME"])
    connection.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (hash_password("s3cret-pass"), SELLER_EMAIL),
    )
    connection.commit()
    connection.close()

    response = client.post(
        "/accounts/login", data={"email": SELLER_EMAIL, "password": "s3cret-pass"}
    )
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["email"] == SELLER_EMAIL


def test_sign_in_with_wrong_password_shows_error(client):
    response = client.post(
        "/accounts/login", data={"email": SELLER_EMAIL, "password": "nope"}
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data
    with client.session_transaction() as session:
        assert "email" not in session


def test_sign_out_clears_the_session(seller_client):
    seller_client.get("/accounts/logout/")
    with seller_client.session_transaction() as session:
        assert "email" not in session


def test_dev_login_is_disabled_by_default(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "ENABLE_DEV_LOGIN", False)
    assert client.get("/dev/skip-login/admin").status_code == 404
    assert b"Development shortcuts" not in client.get("/accounts/login").data


def test_dev_login_works_when_enabled(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "ENABLE_DEV_LOGIN", True)
    assert b"Development shortcuts" in client.get("/accounts/login").data
    response = client.get("/dev/skip-login/seller")
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["email"] == SELLER_EMAIL
