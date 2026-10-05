"""Smoke tests: every primary page renders for the right audience."""

import pytest
from conftest import SEEDED_STATUSES


@pytest.mark.parametrize(
    "path", ["/accounts/login", "/accounts/create", "/how-it-works/"]
)
def test_public_pages_render(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b"TicketVault" in response.data


@pytest.mark.parametrize(
    "path", ["/index", "/seller", "/withdraw", "/secure-withdrawal"]
)
def test_seller_pages_render(seller_client, path):
    assert seller_client.get(path).status_code == 200


def test_dashboard_lists_the_sellers_transactions(seller_client):
    body = seller_client.get("/index").get_data(as_text=True)
    assert "Wisconsin vs Michigan" in body


@pytest.mark.parametrize("transaction_id", range(1, len(SEEDED_STATUSES) + 1))
def test_buyer_offer_page_renders_for_every_status(client, transaction_id):
    assert client.get(f"/ticket/{transaction_id}").status_code == 200


@pytest.mark.parametrize("transaction_id", range(1, len(SEEDED_STATUSES) + 1))
def test_cancelled_page_renders_for_every_status(client, transaction_id):
    assert client.get(f"/cancelled/{transaction_id}").status_code == 200


def test_unknown_transaction_is_not_found(client):
    assert client.get("/ticket/9999").status_code == 404


def test_static_assets_are_served(client):
    assert client.get("/static/css/app.css").status_code == 200
    assert client.get("/static/img/logo-mark.svg").status_code == 200
