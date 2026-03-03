"""Test for matching bug - false positives when external users vote."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, Base, engine
from app.models import Room, Participant, Vote, Movie

# Create fresh database for each test
def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


def test_match_only_counts_current_room_votes(client):
    """
    Bug: Matches should only consider votes from participants in the current room.

    Scenario:
    - Room A has participants P1 and P2
    - Room B has participant P3
    - Movie M exists
    - P1 likes M (Room A)
    - P3 likes M (Room B)

    Expected: Room A should NOT have a match (only P1 liked, P2 didn't)
    Bug: Room A shows a match because voter_ids includes P3 from Room B
    """

    # Create Room A with two participants
    room_a_resp = client.post("/api/v1/rooms")
    room_a_code = room_a_resp.json()["code"]

    # Join Room A as P1
    p1_resp = client.post(f"/api/v1/rooms/{room_a_code}/join", json={"name": "Alice"})
    p1_session = client.cookies.get("session_id")

    # Join Room A as P2 (different session)
    client.cookies.clear()
    p2_resp = client.post(f"/api/v1/rooms/{room_a_code}/join", json={"name": "Bob"})
    p2_session = client.cookies.get("session_id")

    # Create Room B with one participant
    room_b_resp = client.post("/api/v1/rooms")
    room_b_code = room_b_resp.json()["code"]

    # Join Room B as P3
    client.cookies.clear()
    p3_resp = client.post(f"/api/v1/rooms/{room_b_code}/join", json={"name": "Charlie"})
    p3_session = client.cookies.get("session_id")

    # Get movies (seed the database)
    client.cookies.set("session_id", p1_session)
    movies_resp = client.get(f"/api/v1/movies?code={room_a_code}")
    movies = movies_resp.json()
    movie_id = movies[0]["id"]

    # P1 likes the movie (Room A)
    client.post(f"/api/v1/votes?code={room_a_code}", json={"movie_id": movie_id, "liked": True})

    # P3 likes the same movie (Room B)
    client.cookies.set("session_id", p3_session)
    client.post(f"/api/v1/votes?code={room_b_code}", json={"movie_id": movie_id, "liked": True})

    # Check matches for Room A
    client.cookies.set("session_id", p1_session)
    matches_resp = client.get(f"/api/v1/votes/matches?code={room_a_code}")
    matches = matches_resp.json()

    # Room A should NOT have a match - only P1 liked, P2 hasn't voted yet
    # Bug: Room A incorrectly shows a match because P3's vote from Room B is counted
    print(f"Room A matches: {matches}")
    assert len(matches) == 0, f"Expected no matches in Room A, got {len(matches)} matches"


def test_match_requires_all_room_participants(client):
    """
    Correct behavior: A match requires ALL participants in the room to like the movie.

    Scenario:
    - Room has P1 and P2
    - Both like Movie M

    Expected: Match!
    """

    # Create room with two participants
    room_resp = client.post("/api/v1/rooms")
    room_code = room_resp.json()["code"]

    # Join as P1
    p1_resp = client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})
    p1_session = client.cookies.get("session_id")

    # Join as P2
    client.cookies.clear()
    p2_resp = client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Bob"})
    p2_session = client.cookies.get("session_id")

    # Get movies
    client.cookies.set("session_id", p1_session)
    movies_resp = client.get(f"/api/v1/movies?code={room_code}")
    movies = movies_resp.json()
    movie_id = movies[0]["id"]

    # Both like the movie
    client.post(f"/api/v1/votes?code={room_code}", json={"movie_id": movie_id, "liked": True})

    client.cookies.set("session_id", p2_session)
    client.post(f"/api/v1/votes?code={room_code}", json={"movie_id": movie_id, "liked": True})

    # Check matches
    matches_resp = client.get(f"/api/v1/votes/matches?code={room_code}")
    matches = matches_resp.json()

    assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
    assert matches[0]["movie"]["id"] == movie_id


def test_no_match_when_one_dislikes(client):
    """
    Correct behavior: No match if any participant dislikes the movie.

    Scenario:
    - Room has P1 and P2
    - P1 likes Movie M
    - P2 dislikes Movie M

    Expected: No match
    """

    # Create room with two participants
    room_resp = client.post("/api/v1/rooms")
    room_code = room_resp.json()["code"]

    # Join as P1
    p1_resp = client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Alice"})
    p1_session = client.cookies.get("session_id")

    # Join as P2
    client.cookies.clear()
    p2_resp = client.post(f"/api/v1/rooms/{room_code}/join", json={"name": "Bob"})
    p2_session = client.cookies.get("session_id")

    # Get movies
    client.cookies.set("session_id", p1_session)
    movies_resp = client.get(f"/api/v1/movies?code={room_code}")
    movies = movies_resp.json()
    movie_id = movies[0]["id"]

    # P1 likes
    client.post(f"/api/v1/votes?code={room_code}", json={"movie_id": movie_id, "liked": True})

    # P2 dislikes
    client.cookies.set("session_id", p2_session)
    client.post(f"/api/v1/votes?code={room_code}", json={"movie_id": movie_id, "liked": False})

    # Check matches
    matches_resp = client.get(f"/api/v1/votes/matches?code={room_code}")
    matches = matches_resp.json()

    print(f"Matches when one disliked: {matches}")
    assert len(matches) == 0, f"Expected no matches, got {len(matches)}"
