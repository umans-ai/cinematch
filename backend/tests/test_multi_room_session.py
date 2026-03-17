"""Tests for multi-room session handling.

This module tests scenarios where users participate in multiple rooms,
which is a common real-world use case.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


@pytest.fixture
def client():
    """Create a test client with a fresh database."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


class TestMultiRoomParticipation:
    """
    Tests for users participating in multiple movie sessions.

    Users often want to join different rooms for different movie nights
    with different groups of friends.
    """

    def test_invited_user_can_join_existing_room(self, client):
        """
        User A creates a room and shares the code.
        User B should be able to join using the shared code without errors.

        This is the most common flow: creator shares code, friend joins.
        """
        # Alice creates a room
        response = client.post("/api/v1/rooms")
        assert response.status_code == 200
        room_code = response.json()["code"]

        # Alice joins her own room first
        response = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "alice-browser-session"}
        )
        assert response.status_code == 200

        # Bob tries to join using the code Alice shared
        # This should work - he's a new user with a different session
        response = client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Bob"},
            cookies={"session_id": "bob-browser-session"}
        )

        assert response.status_code == 200, (
            f"Expected Bob to join successfully, but got {response.status_code}: "
            f"{response.json().get('detail', 'Unknown error')}"
        )
        assert response.json()["name"] == "Bob"

    def test_user_can_create_and_join_new_room_after_leaving_previous(self, client):
        """
        A user finishes one movie session, then creates/joins another.
        This should work seamlessly.
        """
        # First session
        response1 = client.post("/api/v1/rooms")
        room1_code = response1.json()["code"]

        client.post(
            f"/api/v1/rooms/{room1_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "same-user-session"}
        )

        # Second session (same browser/user)
        response2 = client.post("/api/v1/rooms")
        room2_code = response2.json()["code"]

        # Should be able to join the new room
        response = client.post(
            f"/api/v1/rooms/{room2_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "same-user-session"}
        )

        assert response.status_code == 200, (
            f"User should be able to join new room after previous session. "
            f"Got {response.status_code}: {response.json().get('detail', 'Unknown error')}"
        )
