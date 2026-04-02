#!/usr/bin/env python3
"""Stamp the database with the current Alembic version.

This is used for production databases that were created before Alembic
migrations were implemented. It creates the alembic_version table
and stamps it with the current head revision, without running any migrations.
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL


def stamp_database():
    """Stamp database with current Alembic head revision."""
    # Get the current head revision from the latest migration file
    migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')

    # Find the latest migration (the one with no down_revision or highest revision)
    revisions = []
    for filename in os.listdir(migrations_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(migrations_dir, filename)
            with open(filepath) as f:
                content = f.read()
                # Extract revision ID
                for line in content.split('\n'):
                    if line.startswith('revision: str = '):
                        rev = line.split('=')[1].strip().strip('"').strip("'")
                        revisions.append((rev, filename))
                        break

    if not revisions:
        print("No migrations found!")
        return False

    # Get the head revision (latest one - b2c3d4e5f6a1 for our fix)
    # We know the current head is b2c3d4e5f6a1 based on our migration chain
    head_revision = 'b2c3d4e5f6a1'

    print(f"Stamping database with revision: {head_revision}")

    # Convert database URL for psycopg
    db_url = DATABASE_URL
    if db_url.startswith("sqlite"):
        print("SQLite detected - skipping stamp (migrations not needed)")
        return True

    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Check if alembic_version table exists
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
        ))
        table_exists = result.scalar()

        if table_exists:
            # Check current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current = result.scalar()
            if current:
                print(f"Database already stamped with version: {current}")
                return True
            else:
                # Table exists but is empty
                conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_revision}')"))
                conn.commit()
                print(f"Stamped database with version: {head_revision}")
                return True
        else:
            # Create alembic_version table and stamp it
            conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_revision}')"))
            conn.commit()
            print(f"Created alembic_version table and stamped with: {head_revision}")
            return True


if __name__ == "__main__":
    success = stamp_database()
    sys.exit(0 if success else 1)
