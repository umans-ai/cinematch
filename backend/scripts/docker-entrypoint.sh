#!/bin/bash
set -e

# CineMatch Docker Entrypoint
# Handles database migrations before starting the application

echo "=== CineMatch Startup ==="
echo "Timestamp: $(date)"
echo "Working directory: $(pwd)"

# Check if migrations should run
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo ""
    echo ">>> Running database migrations..."
    uv run python -c "from app.migrations import run_migrations_with_lock; run_migrations_with_lock()"
    echo ">>> Migrations complete"
else
    echo ""
    echo ">>> Skipping migrations (RUN_MIGRATIONS != true)"
fi

echo ""
echo ">>> Starting application..."
echo "Command: $@"
echo ""

# Execute the main command (passed as arguments)
exec "$@"
