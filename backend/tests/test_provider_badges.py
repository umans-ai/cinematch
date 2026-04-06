"""Tests for provider badges displayed on movie cards."""

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


class TestProviderBadges:
    """Tests that movies include provider information for display."""

    def test_movie_includes_available_providers(self, client):
        """
        When getting movies for a room, each movie should include
        the list of providers where it's available.
        """
        # Create room with multiple providers
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337]}  # Netflix + Disney+
        )
        room_code = room_resp.json()["code"]

        # Join room
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        # Get movies
        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        data = movies_resp.json()
        movies = data.get("movies", [])

        # Should have movies
        assert len(movies) > 0

        # Each movie should have available_providers field
        for movie in movies:
            assert "available_providers" in movie
            providers = movie["available_providers"]
            assert isinstance(providers, list)
            assert len(providers) > 0

            # Each provider should have required fields
            for provider in providers:
                assert "id" in provider
                assert "name" in provider
                assert "logo_url" in provider
                assert provider["logo_url"].startswith("https://")

    def test_movie_providers_match_room_providers(self, client):
        """
        Movies should only show providers that are in the room's provider list.
        """
        # Create room with Netflix only
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]}  # Netflix only
        )
        room_code = room_resp.json()["code"]

        # Join room
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        # Get movies
        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        data = movies_resp.json()
        movies = data.get("movies", [])

        # Each movie should only show Netflix as provider
        for movie in movies:
            providers = movie.get("available_providers", [])
            provider_ids = [p["id"] for p in providers]
            # All displayed providers should be in room's list
            for pid in provider_ids:
                assert pid == 8, f"Provider {pid} should not appear in Netflix-only room"

    def test_movie_providers_list_not_empty(self, client):
        """
        Every movie returned should have at least one available provider.
        """
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337, 9]}
        )
        room_code = room_resp.json()["code"]

        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        movies = movies_resp.json().get("movies", [])

        for movie in movies:
            providers = movie.get("available_providers", [])
            assert len(providers) > 0, f"Movie {movie['title']} has no providers"

    def test_single_movie_detail_includes_providers(self, client):
        """
        Getting a single movie by ID should also include provider info.
        """
        # Create room and get movies
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]}
        )
        room_code = room_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        movies = movies_resp.json().get("movies", [])
        assert len(movies) > 0

        # Get first movie detail
        movie_id = movies[0]["id"]
        detail_resp = client.get(f"/api/v1/movies/{movie_id}")
        movie = detail_resp.json()

        # Should have providers
        assert "available_providers" in movie
        assert len(movie["available_providers"]) > 0
