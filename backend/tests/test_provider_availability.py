"""Tests for accurate provider availability recording.

Bug: when fetching movies from TMDB with multiple providers, the backend
records every movie as available on ALL selected providers instead of only
the providers where the movie is actually streaming.

Expected: a movie on Netflix only should NOT show Disney+ or HBO badges.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.models import Movie, MovieAvailability


@pytest.fixture
def client():
    """Create a test client with a fresh database."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def _fake_discover(db, region="US", provider_ids=None, page=1):
    """Fake TMDB discover response with 3 movies."""
    return {
        "results": [
            {
                "id": 1001,
                "title": "Netflix Only Movie",
                "overview": "A movie only on Netflix",
                "release_date": "2024-01-01",
                "poster_path": "/poster1.jpg",
                "genre_ids": [28],
                "vote_average": 7.5,
            },
            {
                "id": 1002,
                "title": "Multi Provider Movie",
                "overview": "A movie on Netflix and Disney+",
                "release_date": "2024-02-01",
                "poster_path": "/poster2.jpg",
                "genre_ids": [12],
                "vote_average": 8.0,
            },
            {
                "id": 1003,
                "title": "Disney Only Movie",
                "overview": "A movie only on Disney+",
                "release_date": "2024-03-01",
                "poster_path": "/poster3.jpg",
                "genre_ids": [16],
                "vote_average": 6.5,
            },
        ],
        "total_pages": 1,
    }


def _fake_movie_details(db, tmdb_id):
    """Fake TMDB movie details with watch/providers data.

    Simulates real TMDB responses where each movie has specific providers:
    - Movie 1001: Netflix only (provider_id=8)
    - Movie 1002: Netflix + Disney+ (provider_ids=8,337)
    - Movie 1003: Disney+ only (provider_id=337)
    """
    provider_map = {
        1001: [{"provider_id": 8, "provider_name": "Netflix"}],
        1002: [
            {"provider_id": 8, "provider_name": "Netflix"},
            {"provider_id": 337, "provider_name": "Disney Plus"},
        ],
        1003: [{"provider_id": 337, "provider_name": "Disney Plus"}],
    }

    return {
        "id": tmdb_id,
        "genres": [{"id": 28, "name": "Action"}],
        "videos": {"results": []},
        "backdrop_path": None,
        "vote_average": 7.0,
        "watch/providers": {
            "results": {
                "US": {
                    "flatrate": provider_map.get(tmdb_id, []),
                },
            },
        },
    }


class TestProviderAvailabilityAccuracy:
    """Movies should only be recorded as available on providers where they actually stream."""

    @patch("app.routers.movies.get_movie_details")
    @patch("app.routers.movies.discover_movies")
    @patch("app.routers.movies.TMDB_API_KEY", "fake-key")
    def test_movie_only_gets_actual_providers(self, mock_discover, mock_details, client):
        """
        A movie available only on Netflix should NOT be recorded as available on Disney+,
        even when the room has both Netflix and Disney+ selected.
        """
        mock_discover.side_effect = _fake_discover
        mock_details.side_effect = _fake_movie_details

        # Create room with Netflix + Disney+
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337]},
        )
        room_code = room_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        # Fetch movies
        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        movies = movies_resp.json()["movies"]

        # Find each movie by title
        movies_by_title = {m["title"]: m for m in movies}

        # Netflix-only movie should only show Netflix
        netflix_movie = movies_by_title["Netflix Only Movie"]
        provider_ids = [p["id"] for p in netflix_movie["available_providers"]]
        assert provider_ids == [8], f"Expected [8], got {provider_ids}"

        # Disney-only movie should only show Disney+
        disney_movie = movies_by_title["Disney Only Movie"]
        provider_ids = [p["id"] for p in disney_movie["available_providers"]]
        assert provider_ids == [337], f"Expected [337], got {provider_ids}"

        # Multi-provider movie should show both
        multi_movie = movies_by_title["Multi Provider Movie"]
        provider_ids = sorted(p["id"] for p in multi_movie["available_providers"])
        assert provider_ids == [8, 337], f"Expected [8, 337], got {provider_ids}"

    @patch("app.routers.movies.get_movie_details")
    @patch("app.routers.movies.discover_movies")
    @patch("app.routers.movies.TMDB_API_KEY", "fake-key")
    def test_existing_movie_preserves_providers_across_rooms(
        self, mock_discover, mock_details, client
    ):
        """
        When a movie already exists from a previous room, creating a new room
        should NOT add all of the new room's providers to that movie.
        """
        mock_discover.side_effect = _fake_discover
        mock_details.side_effect = _fake_movie_details

        # Room 1: Netflix only
        room1_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]},
        )
        room1_code = room1_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room1_code}/join", json={"name": "Alice"})
        client.get(f"/api/v1/movies?code={room1_code}")

        # Room 2: Netflix + Disney+ + HBO
        room2_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337, 384]},
        )
        room2_code = room2_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room2_code}/join", json={"name": "Bob"})
        movies_resp = client.get(f"/api/v1/movies?code={room2_code}")
        movies = movies_resp.json()["movies"]

        movies_by_title = {m["title"]: m for m in movies}

        # Netflix-only movie should still only show Netflix, not HBO
        netflix_movie = movies_by_title["Netflix Only Movie"]
        provider_ids = [p["id"] for p in netflix_movie["available_providers"]]
        assert 384 not in provider_ids, f"HBO should not be on Netflix-only movie: {provider_ids}"
        assert provider_ids == [8], f"Expected [8], got {provider_ids}"

    @patch("app.routers.movies.get_movie_details")
    @patch("app.routers.movies.discover_movies")
    @patch("app.routers.movies.TMDB_API_KEY", "fake-key")
    def test_provider_badges_reflect_real_availability(
        self, mock_discover, mock_details, client
    ):
        """
        With 5 providers selected, movies should show varied provider counts,
        not all 5 on every movie.
        """
        # Extend fake data to include more providers
        def discover_5_providers(db, region="US", provider_ids=None, page=1):
            return _fake_discover(db, region, provider_ids, page)

        def details_5_providers(db, tmdb_id):
            # Movie 1001: Netflix only
            # Movie 1002: Netflix + Disney+
            # Movie 1003: Disney+ only
            return _fake_movie_details(db, tmdb_id)

        mock_discover.side_effect = discover_5_providers
        mock_details.side_effect = details_5_providers

        # Create room with 5 providers
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337, 384, 350, 9]},
        )
        room_code = room_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        movies = movies_resp.json()["movies"]

        # Not every movie should have all 5 providers
        provider_counts = [len(m["available_providers"]) for m in movies]
        assert not all(
            c == 5 for c in provider_counts
        ), f"All movies have 5 providers — availability data is wrong: {provider_counts}"


class TestStaticMovieFallback:
    """When TMDB API is unavailable, static movies should have reasonable provider assignment."""

    @patch("app.routers.movies.TMDB_API_KEY", None)
    def test_static_movies_dont_get_all_providers(self, client):
        """
        Static fallback movies should NOT all have every room provider.
        They use round-robin assignment for variety.
        """
        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8, 337, 384]},
        )
        room_code = room_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        movies_resp = client.get(f"/api/v1/movies?code={room_code}")
        movies = movies_resp.json()["movies"]

        assert len(movies) > 0

        # Not every movie should have all 3 providers
        provider_counts = [len(m["available_providers"]) for m in movies]
        assert not all(
            c == 3 for c in provider_counts
        ), f"All static movies have 3 providers — should use round-robin: {provider_counts}"

    @patch("app.routers.movies.TMDB_API_KEY", None)
    def test_second_room_does_not_corrupt_existing_providers(self, client):
        """
        Creating a second room should NOT add its providers to movies
        that were already seeded for a previous room.
        """
        # Room 1: Netflix only
        room1_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]},
        )
        room1_code = room1_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room1_code}/join", json={"name": "Alice"})
        client.get(f"/api/v1/movies?code={room1_code}")

        # Room 2: Disney+ + HBO
        room2_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [337, 384]},
        )
        room2_code = room2_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room2_code}/join", json={"name": "Bob"})
        movies_resp = client.get(f"/api/v1/movies?code={room2_code}")
        movies = movies_resp.json()["movies"]

        # Movies from room 1 should NOT now have Disney+ and HBO
        # (they were seeded with Netflix via round-robin)
        for movie in movies:
            provider_ids = [p["id"] for p in movie["available_providers"]]
            # Should not have both Disney+ AND HBO on a movie that was Netflix-only
            assert not (
                337 in provider_ids and 384 in provider_ids and 8 in provider_ids
            ), f"Movie '{movie['title']}' has all 3 providers — data was corrupted"
