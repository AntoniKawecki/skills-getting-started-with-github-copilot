from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns successfully"""
    response = client.get("/")
    assert response.status_code == 200  # Should return OK since FastAPI handles the static file

def test_get_activities():
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check structure of an activity
    first_activity = list(data.values())[0]
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity

def test_signup_flow():
    """Test the complete signup flow for an activity"""
    # Get available activities
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Pick first activity
    activity_name = list(activities.keys())[0]
    test_email = "test_student@mergington.edu"
    
    # Try to sign up
    response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify student is in participants list
    response = client.get("/activities")
    assert response.status_code == 200
    updated_activities = response.json()
    assert test_email in updated_activities[activity_name]["participants"]
    
    # Try to sign up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_flow():
    """Test the complete unregister flow for an activity"""
    # First sign up a test student
    activity_name = "Chess Club"
    test_email = "test_unregister@mergington.edu"
    
    # Sign up first
    response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    assert response.status_code == 200
    
    # Verify registration
    response = client.get("/activities")
    activities = response.json()
    assert test_email in activities[activity_name]["participants"]
    
    # Try to unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": test_email})
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    
    # Verify student is removed
    response = client.get("/activities")
    updated_activities = response.json()
    assert test_email not in updated_activities[activity_name]["participants"]
    
    # Try to unregister again (should fail)
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": test_email})
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_invalid_activity():
    """Test handling of invalid activity names"""
    fake_activity = "NonexistentClub"
    test_email = "test@mergington.edu"
    
    # Try to sign up for invalid activity
    response = client.post(f"/activities/{fake_activity}/signup", params={"email": test_email})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    # Try to unregister from invalid activity
    response = client.delete(f"/activities/{fake_activity}/unregister", params={"email": test_email})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]