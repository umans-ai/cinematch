"""
One-time migration script: SQLite to PostgreSQL.

This script migrates data from SQLite to PostgreSQL.
It should be run as a one-off task during the production migration.

Usage:
    python -m scripts.migrate_sqlite_to_postgres --sqlite-path=/tmp/source.db

Environment variables:
    DATABASE_URL: PostgreSQL connection string (required)
"""

import argparse
import logging
import os
import sqlite3
import sys
from pathlib import Path

import psycopg
from psycopg import sql

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Table migration order (respect foreign key dependencies)
TABLES = ['movies', 'rooms', 'participants', 'votes']


def get_sqlite_tables(sqlite_path: str) -> list:
    """Get list of tables from SQLite database."""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_schema_sqlite(sqlite_path: str, table: str) -> list:
    """Get column info for a table."""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [(row[1], row[2]) for row in cursor.fetchall()]  # (name, type)
    conn.close()
    return columns


def migrate_table(sqlite_path: str, pg_conn, table: str) -> int:
    """Migrate a single table from SQLite to PostgreSQL."""
    logger.info(f"Migrating table: {table}")

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Get data from SQLite
    sqlite_cursor.execute(f"SELECT * FROM {table}")
    rows = sqlite_cursor.fetchall()

    if not rows:
        logger.info(f"  Table {table} is empty, skipping")
        sqlite_conn.close()
        return 0

    # Get column names
    columns = [desc[0] for desc in sqlite_cursor.description]
    logger.info(f"  Columns: {columns}")
    logger.info(f"  Rows to migrate: {len(rows)}")

    # Build INSERT query for PostgreSQL
    pg_cursor = pg_conn.cursor()

    # Use parameterized query to prevent SQL injection
    placeholders = ','.join(['%s'] * len(columns))
    columns_quoted = [sql.Identifier(col) for col in columns]

    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
        sql.Identifier(table),
        sql.SQL(', ').join(columns_quoted),
        sql.SQL(placeholders)
    )

    # Insert data in batches
    batch_size = 100
    migrated = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        for row in batch:
            row_data = tuple(row[col] for col in columns)
            pg_cursor.execute(insert_query, row_data)
            migrated += 1

        pg_conn.commit()
        logger.info(f"  Migrated {min(i + batch_size, len(rows))}/{len(rows)} rows")

    sqlite_conn.close()
    logger.info(f"  ✓ Table {table} complete: {migrated} rows")
    return migrated


def verify_migration(sqlite_path: str, pg_conn) -> bool:
    """Verify row counts match between SQLite and PostgreSQL."""
    logger.info("\n=== Verifying Migration ===")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    all_match = True

    for table in TABLES:
        # Get SQLite count
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_count = sqlite_cursor.fetchone()[0]

        # Get PostgreSQL count
        try:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cursor.fetchone()[0]
        except psycopg.errors.UndefinedTable:
            pg_count = 0

        match = sqlite_count == pg_count
        status = "✓" if match else "✗"

        logger.info(f"{status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")

        if not match:
            all_match = False
            logger.error(f"  MISMATCH in {table}: expected {sqlite_count}, got {pg_count}")

    sqlite_conn.close()
    return all_match


def run_alembic_stamp(pg_conn, revision: str = "head"):
    """Stamp the database with the current Alembic revision."""
    logger.info(f"\n=== Stamping Alembic revision: {revision} ===")

    pg_cursor = pg_conn.cursor()

    # Create alembic_version table if not exists
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) PRIMARY KEY
        )
    """)

    # Insert revision
    pg_cursor.execute(
        "INSERT INTO alembic_version (version_num) VALUES (%s) ON CONFLICT (version_num) DO UPDATE SET version_num = %s",
        (revision, revision)
    )
    pg_conn.commit()
    logger.info(f"✓ Database stamped with revision: {revision}")


def main():
    parser = argparse.ArgumentParser(description='Migrate SQLite data to PostgreSQL')
    parser.add_argument('--sqlite-path', required=True, help='Path to SQLite database file')
    parser.add_argument('--alembic-revision', default='head', help='Alembic revision to stamp')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without doing it')
    args = parser.parse_args()

    sqlite_path = args.sqlite_path

    # Verify SQLite file exists
    if not Path(sqlite_path).exists():
        logger.error(f"SQLite database not found: {sqlite_path}")
        sys.exit(1)

    # Get PostgreSQL connection string
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)

    if 'postgresql' not in database_url:
        logger.error(f"DATABASE_URL is not PostgreSQL: {database_url}")
        sys.exit(1)

    logger.info("=== SQLite to PostgreSQL Migration ===")
    logger.info(f"SQLite source: {sqlite_path}")
    logger.info(f"PostgreSQL target: {database_url.split('@')[1] if '@' in database_url else 'hidden'}")

    if args.dry_run:
        logger.info("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Connect to PostgreSQL
    logger.info("\n=== Connecting to PostgreSQL ===")
    pg_conn = psycopg.connect(database_url)

    try:
        # Discover tables in SQLite
        tables = get_sqlite_tables(sqlite_path)
        logger.info(f"Discovered tables: {tables}")

        if args.dry_run:
            # Just show counts
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_cursor = sqlite_conn.cursor()
            for table in tables:
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = sqlite_cursor.fetchone()[0]
                logger.info(f"Would migrate {count} rows from {table}")
            sqlite_conn.close()
            return

        # Run migrations for each table
        logger.info("\n=== Migrating Data ===")
        total_migrated = 0
        for table in TABLES:
            if table in tables:
                count = migrate_table(sqlite_path, pg_conn, table)
                total_migrated += count
            else:
                logger.warning(f"Table {table} not found in SQLite, skipping")

        logger.info(f"\nTotal rows migrated: {total_migrated}")

        # Verify migration
        if not verify_migration(sqlite_path, pg_conn):
            logger.error("\n✗ Migration verification FAILED")
            sys.exit(1)

        # Stamp Alembic version
        run_alembic_stamp(pg_conn, args.alembic_revision)

        logger.info("\n✓ Migration completed successfully!")

    finally:
        pg_conn.close()


if __name__ == '__main__':
    main()
