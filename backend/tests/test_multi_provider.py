"""Tests for multi-provider streaming selection."""

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


class TestMultiProviderSelection:
    """Tests that rooms can have multiple streaming providers."""

    def test_create_room_with_multiple_providers(self, client):
        """
        When creating a room with multiple providers,
        all providers should be stored.
        """
        # Create room with Netflix + Disney+
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337]}  # Netflix + Disney+
        )
        assert room_resp.status_code == 200

        room_data = room_resp.json()
        assert room_data["region"] == "US"
        assert room_data["provider_ids"] == [8, 337]

    def test_create_room_with_single_provider_as_list(self, client):
        """
        Single provider should be stored as a list with one element.
        """
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "FR", "provider_ids": [8]}
        )
        assert room_resp.status_code == 200

        room_data = room_resp.json()
        assert room_data["provider_ids"] == [8]

    def test_room_with_multiple_providers_returns_movies(self, client):
        """
        A room with multiple providers should return movies
        available on at least one of the providers.
        """
        # Create room with Netflix + Disney+
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337]}
        )
        room_code = room_resp.json()["code"]

        # Join room
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        # Get movies
        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        assert movies_resp.status_code == 200

        data = movies_resp.json()
        assert data["room"]["provider_ids"] == [8, 337]
        assert len(data.get("movies", [])) > 0

    def test_cannot_create_room_with_empty_providers(self, client):
        """
        Creating a room with empty provider list should fail validation.
        """
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": []}
        )
        # Should return validation error
        assert room_resp.status_code == 422

    def test_cannot_create_room_with_too_many_providers(self, client):
        """
        Creating a room with more than 5 providers should fail validation.
        """
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 9, 337, 384, 350, 15]}
        )
        # Should return validation error (6 providers > max 5)
        assert room_resp.status_code == 422

    def test_default_room_has_single_provider(self, client):
        """
        Default room creation should have Netflix as single provider.
        """
        room_resp = client.post("/api/v1/rooms")
        assert room_resp.status_code == 200

        room_data = room_resp.json()
        assert room_data["provider_ids"] == [8]  # Netflix default
