"""Database migration runner with PostgreSQL advisory locking."""

import logging
import os

import alembic.config
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Unique advisory lock ID for CineMatch (arbitrary, just needs to be unique)
MIGRATION_LOCK_ID = 54291


def run_migrations_with_lock(max_wait_seconds: int = 300) -> None:
    """
    Run Alembic migrations with PostgreSQL advisory lock.

    Prevents concurrent migration execution during rolling deployments.
    First instance acquires lock and runs migrations.
    Subsequent instances wait for lock release.

    Args:
        max_wait_seconds: Maximum time to wait for lock acquisition

    Raises:
        TimeoutError: If lock cannot be acquired within max_wait_seconds
        Exception: If migration fails
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL not set, skipping migrations")
        return

    # Skip for SQLite (no advisory locks, no concurrent migrations needed)
    if database_url.startswith("sqlite"):
        logger.info("SQLite detected, running migrations without lock")
        _run_alembic_migrations()
        return

    logger.info("PostgreSQL detected, acquiring migration lock...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Try non-blocking lock first (fast path for single instance)
        result = conn.execute(text(f"SELECT pg_try_advisory_lock({MIGRATION_LOCK_ID})"))
        acquired = result.scalar()

        if not acquired:
            logger.info(
                f"Migration lock held by another instance, waiting (max {max_wait_seconds}s)..."
            )

            # Set statement timeout for blocking wait
            conn.execute(text(f"SET statement_timeout = '{max_wait_seconds * 1000}'"))

            try:
                # Blocking wait for lock
                conn.execute(text(f"SELECT pg_advisory_lock({MIGRATION_LOCK_ID})"))
                logger.info("Acquired migration lock after waiting")
            except Exception as e:
                logger.error(f"Failed to acquire migration lock: {e}")
                raise TimeoutError(f"Could not acquire migration lock within {max_wait_seconds}s")

        try:
            logger.info("Running Alembic migrations...")
            _stamp_database_if_needed(conn)
            _run_alembic_migrations()
            logger.info("Migrations completed successfully")
        finally:
            # Always release lock, even if migration fails
            conn.execute(text(f"SELECT pg_advisory_unlock({MIGRATION_LOCK_ID})"))
            logger.info("Released migration lock")


def _stamp_database_if_needed(conn) -> None:
    """
    Stamp database with current Alembic version if tables exist but alembic_version doesn't.

    This handles production databases that were created before Alembic migrations were
    implemented (using SQLAlchemy create_all directly).
    """
    # Check if alembic_version table exists
    result = conn.execute(
        text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'alembic_version')"
        )
    )
    alembic_table_exists = result.scalar()

    if alembic_table_exists:
        # Check if there's a version recorded
        result = conn.execute(text("SELECT COUNT(*) FROM alembic_version"))
        version_count = result.scalar()
        if version_count > 0:
            # Database is already managed by Alembic
            return

    # Check if rooms table exists (indicates database was initialized)
    result = conn.execute(
        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rooms')")
    )
    rooms_table_exists = result.scalar()

    if not rooms_table_exists:
        # Fresh database, let Alembic create everything
        return

    # Check if provider_ids column exists in rooms table
    result = conn.execute(
        text(
            "SELECT EXISTS (SELECT FROM information_schema.columns "
            "WHERE table_name = 'rooms' AND column_name = 'provider_ids')"
        )
    )
    provider_ids_exists = result.scalar()

    # Tables exist but no alembic_version - need to stamp
    logger.info("Database has tables but no alembic_version - stamping with current version...")

    if not alembic_table_exists:
        # Create alembic_version table
        conn.execute(
            text("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """)
        )

    if provider_ids_exists:
        # provider_ids column exists - stamp with latest version
        head_revision = "b2c3d4e5f6a1"  # ensure_provider_ids_data_integrity
        conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_revision}')"))
        conn.commit()
        logger.info(f"Stamped database with version: {head_revision}")
    else:
        # provider_ids column does NOT exist - stamp with version BEFORE that migration
        # This will allow the 81f153f63751 migration to run and add the column
        # The prior revision is fix_participants_unique_constraint
        prior_revision = "6c746b59cf94"
        conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{prior_revision}')"))
        conn.commit()
        logger.info(
            f"Stamped database with version: {prior_revision} (will run provider_ids migration)"
        )


def _run_alembic_migrations() -> None:
    """Execute Alembic upgrade command."""
    # Change to backend directory where alembic.ini is located
    alembic_cfg = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")

    if not os.path.exists(alembic_cfg):
        logger.warning(f"Alembic config not found at {alembic_cfg}, skipping migrations")
        return

    alembic.config.main(argv=["-c", alembic_cfg, "upgrade", "head"])


def check_migration_status() -> dict:
    """Check current migration status."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return {"status": "error", "message": "DATABASE_URL not set"}

    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables "
                    "WHERE table_name = 'alembic_version')"
                )
            )
            has_table = result.scalar()

            if not has_table:
                return {"status": "not_initialized", "current_version": None}

            # Get current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()

            return {
                "status": "ok",
                "current_version": version,
                "database_url_type": (
                    "postgresql" if database_url.startswith("postgresql") else "sqlite"
                ),
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    run_migrations_with_lock()
