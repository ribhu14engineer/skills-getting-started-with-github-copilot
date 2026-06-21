import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_expected_activity_names():
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity_names.issubset(set(data.keys()))
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Art Club"
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_unregisters_existing_student():
    # Arrange
    activity_name = "Programming Class"
    email = "tempstudent@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
