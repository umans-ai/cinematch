"""
Migration integration tests.

Verifies that Alembic migrations work correctly with PostgreSQL:
- upgrade: applies schema changes
- downgrade: reverts schema changes
- idempotency: running twice produces same result
"""

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect


@pytest.fixture(scope="function")
def alembic_cfg(database_url):
    """Create Alembic configuration pointing to test database."""
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg


class TestInitialMigration:
    """Test suite for initial migration."""

    EXPECTED_TABLES = {"rooms", "participants", "votes", "movies", "alembic_version"}

    def test_upgrade_creates_all_tables(self, engine, alembic_cfg):
        """
        given: empty database
        when: run alembic upgrade head
        then: all expected tables are created
        """
        from app.database import Base

        # given - clean slate
        Base.metadata.drop_all(bind=engine)

        # Verify database is empty (except possibly alembic_version)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        assert tables - {"alembic_version"} == set()

        # when
        command.upgrade(alembic_cfg, "head")

        # then
        inspector = inspect(engine)
        actual_tables = set(inspector.get_table_names())
        assert self.EXPECTED_TABLES <= actual_tables

    def test_downgrade_removes_all_tables(self, engine, alembic_cfg):
        """
        given: migrated database
        when: run alembic downgrade -1
        then: all application tables are removed
        """
        # given - migrated database
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(engine)
        assert "rooms" in inspector.get_table_names()

        # when
        command.downgrade(alembic_cfg, "-1")

        # then - application tables removed, alembic_version remains
        inspector = inspect(engine)
        remaining_tables = set(inspector.get_table_names())
        assert "rooms" not in remaining_tables
        assert "participants" not in remaining_tables
        assert "votes" not in remaining_tables
        assert "movies" not in remaining_tables

    def test_upgrade_is_idempotent(self, engine, alembic_cfg):
        """
        given: already migrated database
        when: run upgrade head again
        then: no errors, state remains consistent
        """
        # given
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(engine)
        first_check = set(inspector.get_table_names())

        # when - run upgrade again
        command.upgrade(alembic_cfg, "head")

        # then - tables still exist, no duplicates
        inspector = inspect(engine)
        second_check = set(inspector.get_table_names())
        assert first_check == second_check

    def test_downgrade_upgrade_cycle_restores_schema(self, engine, alembic_cfg):
        """
        given: migrated database
        when: downgrade then upgrade
        then: schema is restored correctly
        """
        # given - migrate and verify
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(engine)
        original_tables = set(inspector.get_table_names())

        # when - full cycle
        command.downgrade(alembic_cfg, "-1")
        command.upgrade(alembic_cfg, "head")

        # then - schema restored
        inspector = inspect(engine)
        restored_tables = set(inspector.get_table_names())
        assert original_tables == restored_tables

    def test_upgrade_preserves_data_integrity(self, engine, alembic_cfg):
        """
        given: fresh database
        when: upgrade is applied and data is inserted
        then: data can be retrieved correctly
        """
        from sqlalchemy.orm import sessionmaker

        from app.database import Base
        from app.models import Room

        Session = sessionmaker(bind=engine)

        # given - migrate
        command.upgrade(alembic_cfg, "head")

        # Add data after migration
        session = Session()
        room = Room(code="TEST", is_active=True)
        session.add(room)
        session.commit()

        # when - retrieve data
        retrieved = session.query(Room).filter_by(code="TEST").first()

        # then - verify data integrity
        assert retrieved is not None
        assert retrieved.code == "TEST"
        assert retrieved.is_active is True

        session.close()
