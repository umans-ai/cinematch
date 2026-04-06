"""Database migration runner with PostgreSQL advisory locking."""

import os

import alembic.config
import structlog
from sqlalchemy import create_engine, text

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger("migrations")

MIGRATION_LOCK_ID = 54291


def run_migrations(max_wait_seconds: int = 300) -> None:
    """Run Alembic migrations with PostgreSQL advisory lock."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL not set, skipping migrations")
        return

    if database_url.startswith("sqlite"):
        logger.info("SQLite detected, running migrations without lock")
        _run_alembic_migrations()
        return

    logger.info("PostgreSQL detected, acquiring migration lock...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT pg_try_advisory_lock({MIGRATION_LOCK_ID})"))
        acquired = result.scalar()

        if not acquired:
            logger.info("Migration lock held, waiting...", max_wait_seconds=max_wait_seconds)
            conn.execute(text(f"SET statement_timeout = '{max_wait_seconds * 1000}'"))
            try:
                conn.execute(text(f"SELECT pg_advisory_lock({MIGRATION_LOCK_ID})"))
                logger.info("Acquired migration lock after waiting")
            except Exception as e:
                logger.error("Failed to acquire migration lock", error=str(e))
                raise TimeoutError(f"Could not acquire migration lock within {max_wait_seconds}s")

        try:
            logger.info("Running Alembic migrations...")
            _run_alembic_migrations()
            logger.info("Migrations completed successfully")
        finally:
            conn.execute(text(f"SELECT pg_advisory_unlock({MIGRATION_LOCK_ID})"))
            logger.info("Released migration lock")


def _run_alembic_migrations() -> None:
    """Execute Alembic upgrade command."""
    alembic_cfg = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")

    if not os.path.exists(alembic_cfg):
        logger.warning("Alembic config not found, skipping migrations", path=alembic_cfg)
        return

    alembic.config.main(argv=["-c", alembic_cfg, "upgrade", "head"])


if __name__ == "__main__":
    run_migrations()
