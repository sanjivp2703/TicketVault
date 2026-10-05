"""JSON endpoints."""


def test_events_can_be_filtered_by_school(client):
    michigan = client.get("/api/events?school=michigan").get_json()
    florida = client.get("/api/events?school=florida").get_json()

    assert michigan and florida
    assert all("Michigan" in event["name"] for event in michigan)
    assert all("Florida" in event["name"] for event in florida)


def test_events_search_matches_name(client):
    events = client.get("/api/events?q=Georgia").get_json()
    assert [event["name"] for event in events] == ["Georgia vs Florida"]
    assert events[0]["datetime"].endswith("03:30 PM")


def test_events_with_unannounced_kickoff_show_tbd(client):
    events = client.get("/api/events?q=Wisconsin").get_json()
    assert events[0]["is_tbd"] == 1
    assert events[0]["datetime"].endswith("at TBD")
