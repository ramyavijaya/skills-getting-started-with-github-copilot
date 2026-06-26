import copy
from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all():
    response = client.get("/activities")

    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_adds_participant():
    new_email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": new_email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for Chess Club"}
    assert new_email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_delete_participant_removes_participant():
    email = "daniel@mergington.edu"
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_delete_missing_participant_returns_404():
    email = "missing@mergington.edu"
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
