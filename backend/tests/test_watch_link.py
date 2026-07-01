"""Tests for persisting and exposing the TMDB region-level "watch" link.

Feature 00028 (Watch Now Deep Links): TMDB's watch/providers response includes a
region-level ``link`` (a "where to watch" page for the movie + region). We persist
it on MovieAvailability and expose it as ``watch_link`` so the frontend can offer a
one-tap "Where to watch" CTA on a match. Graceful null when no link exists.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.models import MovieAvailability


@pytest.fixture
def client():
    """Create a test client with a fresh database."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


# A stable link per (tmdb_id, region) used across the fake responses below.
def _link_for(tmdb_id: int, region: str = "US") -> str:
    return f"https://www.themoviedb.org/movie/{tmdb_id}/watch?locale={region}"


def _fake_discover(db, region="US", provider_ids=None, page=1):
    """Fake TMDB discover response with 2 movies (1 with providers, 1 without)."""
    return {
        "results": [
            {
                "id": 2001,
                "title": "Linked Movie",
                "overview": "A movie streaming on Netflix with a watch link",
                "release_date": "2024-01-01",
                "poster_path": "/poster1.jpg",
                "genre_ids": [28],
                "vote_average": 7.5,
            },
            {
                "id": 2002,
                "title": "No Provider Movie",
                "overview": "A movie with no flatrate providers and no link",
                "release_date": "2024-02-01",
                "poster_path": "/poster2.jpg",
                "genre_ids": [12],
                "vote_average": 6.0,
            },
        ],
        "total_pages": 1,
    }


def _fake_movie_details(db, tmdb_id):
    """Fake TMDB details with a region-level ``link`` for movie 2001 only."""
    region_blocks = {
        2001: {
            "US": {
                "link": _link_for(2001, "US"),
                "flatrate": [{"provider_id": 8, "provider_name": "Netflix"}],
            },
        },
        # 2002: no US entry at all -> no providers, no link
        2002: {},
    }
    return {
        "id": tmdb_id,
        "genres": [{"id": 28, "name": "Action"}],
        "videos": {"results": []},
        "backdrop_path": None,
        "vote_average": 7.0,
        "watch/providers": {"results": region_blocks.get(tmdb_id, {})},
    }


class TestExtractWatchLink:
    """The helper reads the region-level link and is graceful on absence."""

    @patch("app.routers.movies.get_movie_details")
    def test_returns_region_link_when_present(self, mock_details, client):
        from app.database import SessionLocal
        from app.routers.movies import _extract_watch_link

        mock_details.side_effect = _fake_movie_details
        db = SessionLocal()
        try:
            assert _extract_watch_link(db, 2001, "US") == _link_for(2001, "US")
        finally:
            db.close()

    @patch("app.routers.movies.get_movie_details")
    def test_returns_none_when_absent(self, mock_details, client):
        from app.database import SessionLocal
        from app.routers.movies import _extract_watch_link

        mock_details.side_effect = _fake_movie_details
        db = SessionLocal()
        try:
            # No US block for 2002, and unknown region for 2001
            assert _extract_watch_link(db, 2002, "US") is None
            assert _extract_watch_link(db, 2001, "ZZ") is None
        finally:
            db.close()


class TestMoviesEndpointWatchLink:
    """/api/v1/movies exposes watch_link when present, null otherwise."""

    @patch("app.routers.movies.get_movie_details")
    @patch("app.routers.movies.discover_movies")
    @patch("app.routers.movies.TMDB_API_KEY", "fake-key")
    def test_watch_link_present_and_null(self, mock_discover, mock_details, client):
        mock_discover.side_effect = _fake_discover
        mock_details.side_effect = _fake_movie_details

        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]},
        )
        room_code = room_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})

        movies = client.get(f"/api/v1/movies?code={room_code}").json()["movies"]
        by_title = {m["title"]: m for m in movies}

        assert by_title["Linked Movie"]["watch_link"] == _link_for(2001, "US")
        # No-provider movie is only seeded via fallback provider, so it has no TMDB link.
        assert by_title["No Provider Movie"]["watch_link"] is None

    @patch("app.routers.movies.get_movie_details")
    @patch("app.routers.movies.discover_movies")
    @patch("app.routers.movies.TMDB_API_KEY", "fake-key")
    def test_resync_updates_changed_link(self, mock_discover, mock_details, client):
        mock_discover.side_effect = _fake_discover
        mock_details.side_effect = _fake_movie_details

        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]},
        )
        room_code = room_resp.json()["code"]
        client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})
        client.get(f"/api/v1/movies?code={room_code}")

        # TMDB re-indexes: the link for 2001 changes.
        new_link = "https://www.themoviedb.org/movie/2001/watch?locale=US&v=2"

        def _changed_details(db, tmdb_id):
            data = _fake_movie_details(db, tmdb_id)
            if tmdb_id == 2001:
                data["watch/providers"]["results"]["US"]["link"] = new_link
            return data

        mock_details.side_effect = _changed_details
        # Force a re-fetch which re-records availability for existing movies.
        client.get(f"/api/v1/movies?code={room_code}&refresh=true")

        from app.database import SessionLocal
        from app.models import Movie

        db = SessionLocal()
        try:
            movie = db.query(Movie).filter(Movie.tmdb_id == 2001).first()
            rows = (
                db.query(MovieAvailability)
                .filter(
                    MovieAvailability.movie_id == movie.id,
                    MovieAvailability.provider_id == 8,
                )
                .all()
            )
            assert any(r.link == new_link for r in rows)
        finally:
            db.close()


class TestMatchesWatchLink:
    """/api/v1/votes/matches includes watch_link and available_providers."""

    @patch("app.routers.movies.get_movie_details")
    @patch("app.routers.movies.discover_movies")
    @patch("app.routers.movies.TMDB_API_KEY", "fake-key")
    def test_match_exposes_watch_link_and_providers(self, mock_discover, mock_details, client):
        mock_discover.side_effect = _fake_discover
        mock_details.side_effect = _fake_movie_details

        room_resp = client.post(
            "/api/v1/rooms",
            json={"region": "US", "provider_ids": [8]},
        )
        room_code = room_resp.json()["code"]

        # Two participants both like the linked movie.
        client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Alice"},
            cookies={"session_id": "alice-session"},
        )
        client.post(
            f"/api/v1/rooms/{room_code}/join",
            json={"name": "Bob"},
            cookies={"session_id": "bob-session"},
        )

        movies = client.get(f"/api/v1/movies?code={room_code}").json()["movies"]
        linked = next(m for m in movies if m["title"] == "Linked Movie")

        for session in ("alice-session", "bob-session"):
            client.post(
                f"/api/v1/votes?code={room_code}",
                json={"movie_id": linked["id"], "liked": True},
                cookies={"session_id": session},
            )

        matches = client.get(f"/api/v1/votes/matches?code={room_code}").json()
        assert len(matches) == 1
        match_movie = matches[0]["movie"]
        assert match_movie["watch_link"] == _link_for(2001, "US")
        assert [p["id"] for p in match_movie["available_providers"]] == [8]
