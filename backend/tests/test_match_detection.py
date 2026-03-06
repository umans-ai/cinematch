"""Tests for match detection between participants."""

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


@pytest.fixture
def setup_room_with_two_users(client):
    """Create a room with two participants and some movies."""
    # Create room
    response = client.post("/api/v1/rooms")
    room_code = response.json()["code"]

    # Add participants
    response1 = client.post(
        f"/api/v1/rooms/{room_code}/join",
        json={"name": "Alice"},
        cookies={"session_id": "alice-session"}
    )
    alice_id = response1.json()["id"]

    response2 = client.post(
        f"/api/v1/rooms/{room_code}/join",
        json={"name": "Bob"},
        cookies={"session_id": "bob-session"}
    )
    bob_id = response2.json()["id"]

    # Seed some movies (they'll be fetched from TMDB or use existing)
    response = client.get(f"/api/v1/movies?code={room_code}")
    data = response.json()
    movies = data.get("movies", [])

    return {
        "room_code": room_code,
        "alice_id": alice_id,
        "bob_id": bob_id,
        "movies": movies
    }


class TestMatchDetection:
    """Tests for detecting matches between participants."""

    def test_match_detected_when_both_participants_like_same_movie(
        self, client, setup_room_with_two_users
    ):
        """
        When both participants like the same movie, it should appear in matches.
        """
        data = setup_room_with_two_users
        room_code = data["room_code"]
        movies = data["movies"]

        if not movies:
            pytest.skip("No movies available in database")

        movie = movies[0]

        # Alice likes the movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie["id"], "liked": True},
            cookies={"session_id": "alice-session"}
        )

        # Bob likes the same movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie["id"], "liked": True},
            cookies={"session_id": "bob-session"}
        )

        # Check matches endpoint
        response = client.get(f"/api/v1/votes/matches?code={room_code}")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 1, f"Expected 1 match but got {len(matches)}"
        assert matches[0]["movie"]["id"] == movie["id"]
        assert "Alice" in matches[0]["participants"]
        assert "Bob" in matches[0]["participants"]

    def test_no_match_when_participants_disagree(
        self, client, setup_room_with_two_users
    ):
        """
        When participants disagree on a movie, it should not appear in matches.
        """
        data = setup_room_with_two_users
        room_code = data["room_code"]
        movies = data["movies"]

        if not movies:
            pytest.skip("No movies available in database")

        movie = movies[0]

        # Alice likes the movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie["id"], "liked": True},
            cookies={"session_id": "alice-session"}
        )

        # Bob dislikes the same movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie["id"], "liked": False},
            cookies={"session_id": "bob-session"}
        )

        # Check matches endpoint
        response = client.get(f"/api/v1/votes/matches?code={room_code}")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 0, f"Expected 0 matches but got {len(matches)}"

    def test_multiple_matches_detected(
        self, client, setup_room_with_two_users
    ):
        """
        When participants like multiple movies in common, all should appear in matches.
        """
        data = setup_room_with_two_users
        room_code = data["room_code"]
        movies = data["movies"]

        if len(movies) < 2:
            pytest.skip("Need at least 2 movies for this test")

        movie1, movie2 = movies[0], movies[1]

        # Both like first movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie1["id"], "liked": True},
            cookies={"session_id": "alice-session"}
        )
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie1["id"], "liked": True},
            cookies={"session_id": "bob-session"}
        )

        # Both like second movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie2["id"], "liked": True},
            cookies={"session_id": "alice-session"}
        )
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie2["id"], "liked": True},
            cookies={"session_id": "bob-session"}
        )

        # Check matches endpoint
        response = client.get(f"/api/v1/votes/matches?code={room_code}")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 2, f"Expected 2 matches but got {len(matches)}"

    def test_single_participant_cannot_create_match(
        self, client, setup_room_with_two_users
    ):
        """
        A single participant liking movies should not create any matches.
        """
        data = setup_room_with_two_users
        room_code = data["room_code"]
        movies = data["movies"]

        if not movies:
            pytest.skip("No movies available in database")

        movie = movies[0]

        # Only Alice likes the movie
        client.post(
            f"/api/v1/votes?code={room_code}",
            json={"movie_id": movie["id"], "liked": True},
            cookies={"session_id": "alice-session"}
        )

        # Check matches endpoint - should be empty with only one vote
        response = client.get(f"/api/v1/votes/matches?code={room_code}")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 0, f"Expected 0 matches with single participant but got {len(matches)}"
