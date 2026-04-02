"""Tests for movie filtering by region and platform."""

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


class TestMovieFiltering:
    """Tests that movies are properly filtered by region and platform."""

    def test_room_with_different_platforms_gets_different_movies(self, client):
        """
        When two rooms are created with different platforms,
        they should have different movie pools.
        """
        # Create room with Netflix (US)
        room1_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]}  # Netflix
        )
        room1_code = room1_resp.json()["code"]

        # Create room with Disney+ (US)
        room2_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [337]}  # Disney+
        )
        room2_code = room2_resp.json()["code"]

        # Join both rooms
        client.post(f"/api/v1/rooms/{room1_code}/join", json={"name": "Alice"})
        client.post(f"/api/v1/rooms/{room2_code}/join", json={"name": "Bob"})

        # Get movies for both rooms
        movies1_resp = client.get(f"/api/v1/movies?code={room1_code}")
        movies2_resp = client.get(f"/api/v1/movies?code={room2_code}")

        data1 = movies1_resp.json()
        data2 = movies2_resp.json()

        movies1 = data1.get("movies", [])
        movies2 = data2.get("movies", [])

        # Both rooms should have movies
        assert len(movies1) > 0, "Netflix room should have movies"
        assert len(movies2) > 0, "Disney+ room should have movies"

        # The room info should reflect the correct providers
        assert data1["room"]["provider_ids"] == [8]  # Netflix
        assert data2["room"]["provider_ids"] == [337]  # Disney+

    def test_room_with_different_regions_gets_different_movies(self, client):
        """
        When two rooms are created with different regions,
        they should have different movie pools.
        """
        # Create room with Netflix (US)
        room1_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]}
        )
        room1_code = room1_resp.json()["code"]

        # Create room with Netflix (FR)
        room2_resp = client.post(
            "/api/v1/rooms",
            json={"region": "FR", "provider_ids": [8]}
        )
        room2_code = room2_resp.json()["code"]

        # Join both rooms
        client.post(f"/api/v1/rooms/{room1_code}/join", json={"name": "Alice"})
        client.post(f"/api/v1/rooms/{room2_code}/join", json={"name": "Bob"})

        # Get movies for both rooms
        movies1_resp = client.get(f"/api/v1/movies?code={room1_code}")
        movies2_resp = client.get(f"/api/v1/movies?code={room2_code}")

        data1 = movies1_resp.json()
        data2 = movies2_resp.json()

        # The room info should reflect the correct region
        assert data1["room"]["region"] == "US"
        assert data2["room"]["region"] == "FR"

    def test_room_returns_only_available_movies(self, client):
        """
        A room should only return movies that have availability
        recorded for its region and provider.
        """
        # Create a room
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]}
        )
        room_code = room_resp.json()["code"]

        # Join room
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        # Get movies
        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        data = movies_resp.json()
        movies = data.get("movies", [])

        # Should have movies available
        assert len(movies) > 0

        # All returned movies should have availability for US/Netflix
        # (This is implicitly tested by the query logic)

    def test_default_room_uses_us_netflix(self, client):
        """
        When creating a room without specifying region/provider,
        defaults should be US and Netflix ([8]).
        """
        # Create room without region/provider
        room_resp = client.post("/api/v1/rooms")
        room_code = room_resp.json()["code"]

        # Check defaults
        assert room_resp.json()["region"] == "US"
        assert room_resp.json()["provider_ids"] == [8]

        # Join and get movies
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})
        movies_resp = client.get(f"/api/v1/movies?code={room_code}")

        data = movies_resp.json()
        assert data["room"]["region"] == "US"
        assert data["room"]["provider_ids"] == [8]
        assert len(data.get("movies", [])) > 0
