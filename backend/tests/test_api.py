from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

# Initialize database before creating test client
init_db()

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_room():
    response = client.post("/api/v1/rooms")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert len(data["code"]) == 4
    assert data["is_active"] is True


def test_get_room():
    # Create room first
    create_resp = client.post("/api/v1/rooms")
    code = create_resp.json()["code"]

    # Get room
    get_resp = client.get(f"/api/v1/rooms/{code}")
    assert get_resp.status_code == 200
    assert get_resp.json()["code"] == code


def test_join_room():
    # Create room
    create_resp = client.post("/api/v1/rooms")
    code = create_resp.json()["code"]

    # Join room
    join_resp = client.post(
        f"/api/v1/rooms/{code}/join",
        json={"name": "Alice"}
    )
    assert join_resp.status_code == 200
    assert join_resp.json()["name"] == "Alice"
