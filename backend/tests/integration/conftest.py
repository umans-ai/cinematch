"""
Integration test fixtures for PostgreSQL persistence tests.

Uses testcontainers to spin up ephemeral PostgreSQL containers.
Tests should follow given/when/then pattern and read like executable documentation.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.database import Base


@pytest.fixture(scope="function")
def postgres_container():
    """Start PostgreSQL container for each test function."""
    postgres = PostgresContainer("postgres:16-alpine")
    postgres.start()

    # Wait for PostgreSQL to be ready
    import time
    import psycopg

    port = postgres.get_exposed_port(5432)
    for _ in range(10):
        try:
            conn = psycopg.connect(
                host="localhost",
                port=port,
                user="test",
                password="test",
                dbname="test",
            )
            conn.close()
            break
        except psycopg.OperationalError:
            time.sleep(0.5)

    yield postgres
    postgres.stop()


@pytest.fixture(scope="function")
def database_url(postgres_container):
    """Get the database URL from the running container using psycopg 3 driver."""
    # Build URL manually for psycopg 3 compatibility
    # testcontainers.get_connection_url() returns psycopg2 URL by default
    port = postgres_container.get_exposed_port(5432)
    return f"postgresql+psycopg://test:test@localhost:{port}/test"


@pytest.fixture(scope="function")
def engine(database_url):
    """Create SQLAlchemy engine connected to PostgreSQL."""
    eng = create_engine(database_url, pool_pre_ping=True)
    yield eng
    eng.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Create a fresh database session for each test.

    Drops and recreates all tables before each test to ensure isolation.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
