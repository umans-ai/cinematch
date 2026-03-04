"""Tests for room participation and session handling."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, Base, engine
from app.models import Room, Participant


@pytest.fixture
def client():
    """Create a test client with a fresh database."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


class TestRoomParticipation:
    """Tests for room participation workflows."""

    def test_user_can_join_different_rooms_with_same_session(self, client):
        """
        A user should be able to join multiple different rooms using the same session.
        This is important for users who want to participate in different movie sessions.
        """
        # Create first room
        response1 = client.post("/api/v1/rooms")
        assert response1.status_code == 200
        room1_code = response1.json()["code"]

        # Join first room
        response2 = client.post(
            f"//api/v1/rooms/{room1_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "test-session-123"}
        )
        assert response2.status_code == 200

        # Create second room
        response3 = client.post("/api/v1/rooms")
        assert response3.status_code == 200
        room2_code = response3.json()["code"]

        # Join second room with same session - this should work
        response4 = client.post(
            f"/api/v1/rooms/{room2_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "test-session-123"}
        )
        assert response4.status_code == 200, f"Expected 200 but got {response4.status_code}: {response4.text}"
        assert response4.json()["room_id"] != response2.json()["room_id"]

    def test_second_user_can_join_existing_room(self, client):
        """
        A second participant should be able to join an existing room that has one participant.
        """
        # Create room
        response1 = client.post("/api/v1/rooms")
        room_code = response1.json()["code"]

        # First user joins
        response2 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "session-alice"}
        )
        assert response2.status_code == 200

        # Second user joins with different session - should work
        response3 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Bob"},
            cookies={"session_id": "session-bob"}
        )
        assert response3.status_code == 200, f"Expected 200 but got {response3.status_code}: {response3.text}"
        assert response3.json()["name"] == "Bob"

    def test_room_accepts_up_to_two_participants(self, client):
        """
        A room should accept exactly two participants and then be full.
        """
        response1 = client.post("/api/v1/rooms")
        room_code = response1.json()["code"]

        # First participant
        response2 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "session-1"}
        )
        assert response2.status_code == 200

        # Second participant
        response3 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Bob"},
            cookies={"session_id": "session-2"}
        )
        assert response3.status_code == 200

        # Third participant should fail
        response4 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Charlie"},
            cookies={"session_id": "session-3"}
        )
        assert response4.status_code == 400
        assert "full" in response4.json()["detail"].lower()

    def test_same_user_can_rejoin_same_room(self, client):
        """
        A user rejoining the same room should be recognized as existing participant.
        """
        response1 = client.post("/api/v1/rooms")
        room_code = response1.json()["code"]

        # First join
        response2 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "same-session"}
        )
        assert response2.status_code == 200
        participant_id = response2.json()["id"]

        # Rejoin with same session
        response3 = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "same-session"}
        )
        assert response3.status_code == 200
        assert response3.json()["id"] == participant_id
