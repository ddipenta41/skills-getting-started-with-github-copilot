import copy

from fastapi.testclient import TestClient

from src.app import app, activities


def client_fixture():
    orig = copy.deepcopy(activities)
    with TestClient(app) as client:
        yield client
    # restore original state
    activities.clear()
    activities.update(orig)


def test_get_activities():
    orig = copy.deepcopy(activities)
    with TestClient(app) as client:
        resp = client.get("/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
    activities.clear()
    activities.update(orig)


def test_signup_and_duplicate():
    orig = copy.deepcopy(activities)
    with TestClient(app) as client:
        email = "testuser@example.com"
        # signup should succeed
        resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert resp.status_code == 200
        assert "Signed up" in resp.json().get("message", "")

        # duplicate signup should fail
        resp2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert resp2.status_code == 400
        # Accept either wording for the duplicate signup detail
        detail = resp2.json().get("detail", "").lower()
        assert "already" in detail or "already signed up" in detail

    activities.clear()
    activities.update(orig)


def test_delete_participant():
    orig = copy.deepcopy(activities)
    with TestClient(app) as client:
        email = "tobedeleted@example.com"
        # ensure present by signing up
        resp = client.post(f"/activities/Programming%20Class/signup?email={email}")
        assert resp.status_code == 200

        # delete
        resp2 = client.delete(f"/activities/Programming%20Class/participants?email={email}")
        assert resp2.status_code == 200
        assert "Removed" in resp2.json().get("message", "")

        # confirm removed
        resp3 = client.get("/activities")
        assert email not in resp3.json()["Programming Class"]["participants"]

    activities.clear()
    activities.update(orig)
