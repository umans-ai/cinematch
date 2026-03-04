"""Tests for TMDB service client and caching."""
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import TMDBCache
from app.services.tmdb import CachedTMDBClient, TMDBClient


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mock_discover_response():
    return {
        "results": [
            {
                "id": 550,
                "title": "Fight Club",
                "release_date": "1999-10-15",
                "overview": "An insomniac office worker...",
                "poster_path": "/poster.jpg",
                "backdrop_path": "/backdrop.jpg",
                "vote_average": 8.4,
                "genre_ids": [18, 53],
            }
        ],
        "total_pages": 10,
        "total_results": 200,
    }


@pytest.fixture
def mock_details_response():
    return {
        "id": 550,
        "title": "Fight Club",
        "release_date": "1999-10-15",
        "overview": "An insomniac office worker...",
        "poster_path": "/poster.jpg",
        "backdrop_path": "/backdrop.jpg",
        "vote_average": 8.4,
        "genres": [{"id": 18, "name": "Drama"}],
        "videos": {
            "results": [
                {"key": "SUXWAEX2jlg", "site": "YouTube", "type": "Trailer"}
            ]
        },
    }


# --- TMDBClient (pure HTTP, no cache) ---


def test_discover_movies_calls_correct_url(mock_discover_response):
    client = TMDBClient(api_key="test_key")
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_discover_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp) as mock_get:
        result = client.discover_movies(region="US", provider=8, page=1)

    call_args = mock_get.call_args
    assert "/discover/movie" in call_args[0][0]
    assert call_args[1]["params"]["watch_region"] == "US"
    assert call_args[1]["params"]["with_watch_providers"] == 8


def test_discover_movies_returns_results_list(mock_discover_response):
    client = TMDBClient(api_key="test_key")
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_discover_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp):
        result = client.discover_movies()

    assert len(result) == 1
    assert result[0]["title"] == "Fight Club"
    assert result[0]["id"] == 550


def test_get_movie_details_appends_videos(mock_details_response):
    client = TMDBClient(api_key="test_key")
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_details_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp) as mock_get:
        result = client.get_movie_details(550)

    call_args = mock_get.call_args
    assert "/movie/550" in call_args[0][0]
    assert "videos" in call_args[1]["params"]["append_to_response"]
    assert result["videos"]["results"][0]["key"] == "SUXWAEX2jlg"


# --- CachedTMDBClient (wraps TMDBClient with SQLite cache) ---


def test_cached_client_stores_result_in_cache(db, mock_discover_response):
    client = CachedTMDBClient(api_key="test_key", db=db)
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_discover_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp):
        client.discover_movies(region="US", provider=8, page=1)

    entry = db.query(TMDBCache).filter(TMDBCache.key == "discover:US:8:1").first()
    assert entry is not None
    assert "Fight Club" in entry.data


def test_cached_client_uses_cache_on_second_call(db, mock_discover_response):
    client = CachedTMDBClient(api_key="test_key", db=db)
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_discover_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp) as mock_get:
        client.discover_movies(region="US", provider=8, page=1)
        client.discover_movies(region="US", provider=8, page=1)

    # httpx.get called only once — second call used cache
    assert mock_get.call_count == 1


def test_cached_client_refetches_when_cache_expired(db, mock_discover_response):
    client = CachedTMDBClient(api_key="test_key", db=db)

    # Seed an expired cache entry (25h ago)
    expired_time = datetime.now(timezone.utc) - timedelta(hours=25)
    entry = TMDBCache(
        key="discover:US:8:1",
        data=json.dumps([{"title": "Old Movie"}]),
        cached_at=expired_time,
    )
    db.add(entry)
    db.commit()

    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_discover_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp) as mock_get:
        result = client.discover_movies(region="US", provider=8, page=1)

    assert mock_get.call_count == 1
    assert result[0]["title"] == "Fight Club"


def test_cached_client_get_movie_details(db, mock_details_response):
    client = CachedTMDBClient(api_key="test_key", db=db)
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_details_response
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_resp):
        result = client.get_movie_details(550)

    assert result["title"] == "Fight Club"
    entry = db.query(TMDBCache).filter(TMDBCache.key == "details:550").first()
    assert entry is not None
