from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
}

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update({
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": list(details["participants"]),
        }
        for name, details in INITIAL_ACTIVITIES.items()
    })
    yield


def test_get_activities_returns_activities():
    # Arrange: Test client and baseline data are set up by fixture.
    # Act:
    response = client.get("/activities")
    # Assert:
    assert response.status_code == 200
    json_data = response.json()
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data
    assert json_data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_success():
    # Arrange:
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    # Act:
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert:
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange:
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    # Act:
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")
    # Assert:
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    # Arrange:
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act:
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    # Assert:
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found_returns_404():
    # Arrange:
    activity_name = "Chess Club"
    email = "notfound@mergington.edu"
    # Act:
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    # Assert:
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
