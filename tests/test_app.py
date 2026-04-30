import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


class TestActivitiesAPI:
    """Test cases for the Activities API endpoints"""

    def test_get_activities(self):
        """Test GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()

        # Check that we get the expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        # Use an activity that has space for participants
        activity_name = "Basketball Team"
        email = "test@student.edu"

        # Ensure the student is not already signed up
        assert email not in activities[activity_name]["participants"]

        response = client.post(f"/activities/{activity_name}/signup", json={"email": email})
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was added
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post("/activities/NonExistentActivity/signup", json={"email": "test@test.com"})
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self):
        """Test signup when student is already signed up"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        response = client.post(f"/activities/{activity_name}/signup", json={"email": email})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up" in data["detail"]

    def test_remove_participant_successful(self):
        """Test successful removal of a participant"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in participants

        # Verify they're currently signed up
        assert email in activities[activity_name]["participants"]

        response = client.delete(f"/activities/{activity_name}/participants", json={"email": email})
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was removed
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_activity_not_found(self):
        """Test removal from non-existent activity"""
        response = client.delete("/activities/NonExistentActivity/participants", json={"email": "test@test.com"})
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self):
        """Test removal of participant not in activity"""
        activity_name = "Art Club"
        email = "notparticipating@test.com"

        # Ensure they're not in the activity
        assert email not in activities[activity_name]["participants"]

        response = client.delete(f"/activities/{activity_name}/participants", json={"email": email})
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_root_redirect(self):
        """Test root endpoint redirects to static index"""
        response = client.get("/")
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers.get("location", "")