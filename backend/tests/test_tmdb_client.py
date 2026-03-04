from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, init_db
from app.main import app
from app.models import Movie

# Isolated SQLite DB for these tests
_engine = create_engine("sqlite:///./test_tmdb.db", connect_args={"check_same_thread": False})
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
Base.metadata.create_all(bind=_engine)


def override_get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


MOCK_DISCOVER_RESULTS = [
    {
        "id": 550,
        "title": "Fight Club",
        "release_date": "1999-10-15",
        "genre_ids": [18, 53],
        "poster_path": "/pB8BM7pdSp6B6Ih7QI4S2t0POoT.jpg",
        "backdrop_path": "/hZkgoQYus5dXo3H8T7Uef6DNknx.jpg",
        "overview": "A ticking-Loss, bored insomniac...",
        "vote_average": 8.4,
        "popularity": 73.5,
    },
    {
        "id": 680,
        "title": "Pulp Fiction",
        "release_date": "1994-09-10",
        "genre_ids": [80, 53],
        "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "overview": "The lives of two mob hitmen...",
        "vote_average": 8.5,
        "popularity": 65.2,
    },
]

MOCK_DETAILS_RESPONSE = {
    "id": 550,
    "title": "Fight Club",
    "release_date": "1999-10-15",
    "overview": "A ticking-Loss, bored insomniac...",
    "poster_path": "/pB8BM7pdSp6B6Ih7QI4S2t0POoT.jpg",
    "backdrop_path": "/hZkgoQYus5dXo3H8T7Uef6DNknx.jpg",
    "vote_average": 8.4,
    "popularity": 73.5,
    "genres": [{"id": 18, "name": "Drama"}, {"id": 53, "name": "Thriller"}],
    "videos": {
        "results": [
            {"key": "SUXWAEX2jlg", "site": "YouTube", "type": "Trailer"},
            {"key": "other123", "site": "YouTube", "type": "Teaser"},
        ]
    },
}


def _mock_httpx_get(url, **kwargs):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    if "discover" in url:
        mock_resp.json.return_value = {"results": MOCK_DISCOVER_RESULTS}
    elif "/movie/" in url:
        mock_resp.json.return_value = MOCK_DETAILS_RESPONSE
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@pytest.fixture(autouse=True)
def clean_db():
    """Reset DB between tests."""
    db = _Session()
    db.query(Movie).delete()
    db.commit()
    db.close()
    yield
    db = _Session()
    db.query(Movie).delete()
    db.commit()
    db.close()


class TestTMDBClient:
    def test_tmdb_client_discover_returns_movies(self):
        from app.services.tmdb import TMDBClient

        with patch("app.services.tmdb.httpx.Client") as mock_cls:
            ctx = MagicMock()
            ctx.__enter__ = MagicMock(return_value=ctx)
            ctx.__exit__ = MagicMock(return_value=False)
            ctx.get.side_effect = _mock_httpx_get
            mock_cls.return_value = ctx

            movies = TMDBClient("fake-key").discover_movies(region="US", page=1)
            assert len(movies) == 2
            assert movies[0]["title"] == "Fight Club"

    def test_tmdb_client_get_details_extracts_trailer(self):
        from app.services.tmdb import TMDBClient

        with patch("app.services.tmdb.httpx.Client") as mock_cls:
            ctx = MagicMock()
            ctx.__enter__ = MagicMock(return_value=ctx)
            ctx.__exit__ = MagicMock(return_value=False)
            ctx.get.side_effect = _mock_httpx_get
            mock_cls.return_value = ctx

            details = TMDBClient("fake-key").get_movie_details(550)
            assert details["trailer_key"] == "SUXWAEX2jlg"
            assert details["genre"] == "Drama, Thriller"
            assert details["year"] == 1999

    def test_sync_movies_creates_new_rows(self):
        from app.services.tmdb import sync_movies_to_db

        db = _Session()
        try:
            with patch("app.services.tmdb.TMDBClient") as mock_cls:
                mock_cls.return_value.discover_movies.return_value = MOCK_DISCOVER_RESULTS
                result = sync_movies_to_db(db, "fake-key", region="US", pages=1)

            assert len(result) == 2
            fight_club = db.query(Movie).filter(Movie.tmdb_id == 550).first()
            assert fight_club is not None
            assert fight_club.title == "Fight Club"
            assert fight_club.poster_path == "/pB8BM7pdSp6B6Ih7QI4S2t0POoT.jpg"
        finally:
            db.close()

    def test_sync_movies_skips_fresh_cache(self):
        from app.services.tmdb import sync_movies_to_db

        db = _Session()
        try:
            movie = Movie(tmdb_id=550, title="Fight Club (cached)", cached_at=datetime.now(timezone.utc))
            db.add(movie)
            db.commit()

            with patch("app.services.tmdb.TMDBClient") as mock_cls:
                mock_cls.return_value.discover_movies.return_value = [MOCK_DISCOVER_RESULTS[0]]
                result = sync_movies_to_db(db, "fake-key", region="US", pages=1)

            assert len(result) == 1
            assert result[0].title == "Fight Club (cached)"
        finally:
            db.close()

    def test_sync_movies_refreshes_stale_cache(self):
        from app.services.tmdb import sync_movies_to_db

        db = _Session()
        try:
            movie = Movie(
                tmdb_id=550,
                title="Fight Club (stale)",
                cached_at=datetime.now(timezone.utc) - timedelta(hours=25),
            )
            db.add(movie)
            db.commit()

            with patch("app.services.tmdb.TMDBClient") as mock_cls:
                mock_cls.return_value.discover_movies.return_value = [MOCK_DISCOVER_RESULTS[0]]
                result = sync_movies_to_db(db, "fake-key", region="US", pages=1)

            assert len(result) == 1
            assert result[0].title == "Fight Club"
        finally:
            db.close()


class TestMovieEndpoints:
    def _create_room(self) -> str:
        return client.post("/api/v1/rooms").json()["code"]

    def test_get_movies_with_tmdb_key(self):
        code = self._create_room()

        with patch("app.routers.movies.get_tmdb_api_key", return_value="fake-key"), \
             patch("app.routers.movies.sync_movies_to_db") as mock_sync:
            m = MagicMock()
            m.id = 1
            m.title = "TMDB Movie"
            m.year = 2024
            m.genre = "Action"
            m.poster_url = None
            m.description = "A movie"
            m.tmdb_id = 123
            m.poster_path = "/poster.jpg"
            m.backdrop_path = "/backdrop.jpg"
            m.vote_average = 7.5
            mock_sync.return_value = [m]

            resp = client.get(f"/api/v1/movies?code={code}")
            assert resp.status_code == 200
            assert resp.json()[0]["title"] == "TMDB Movie"
            assert resp.json()[0]["tmdb_id"] == 123

    def test_get_movies_without_key_falls_back_to_static(self):
        code = self._create_room()
        with patch("app.routers.movies.get_tmdb_api_key", return_value=None):
            resp = client.get(f"/api/v1/movies?code={code}")
            assert resp.status_code == 200
            assert len(resp.json()) > 0
            assert resp.json()[0]["tmdb_id"] is None

    def test_get_movie_detail_fetches_trailer(self):
        db = _Session()
        try:
            movie = Movie(title="Test Movie", tmdb_id=9999, year=1999)
            db.add(movie)
            db.commit()
            db.refresh(movie)
            movie_id = movie.id
        finally:
            db.close()

        with patch("app.routers.movies.get_tmdb_api_key", return_value="fake-key"), \
             patch("app.routers.movies.TMDBClient") as mock_cls:
            mock_cls.return_value.get_movie_details.return_value = {
                "trailer_key": "SUXWAEX2jlg",
                "genre": "Drama, Thriller",
                "overview": "Full overview...",
            }
            resp = client.get(f"/api/v1/movies/{movie_id}")
            assert resp.status_code == 200
            assert resp.json()["trailer_key"] == "SUXWAEX2jlg"

    def test_movie_model_new_fields_nullable(self):
        db = _Session()
        try:
            movie = Movie(title="Minimal Movie")
            db.add(movie)
            db.commit()
            db.refresh(movie)

            assert movie.tmdb_id is None
            assert movie.poster_path is None
            assert movie.backdrop_path is None
            assert movie.overview is None
            assert movie.vote_average is None
            assert movie.trailer_key is None
            assert movie.popularity is None
            assert movie.cached_at is None
        finally:
            db.close()
