# Local dev: fast feedback loop with PostgreSQL in Docker, code running locally
dev-local:
    #!/usr/bin/env bash
    set -e
    echo "🚀 Starting local dev environment..."
    echo ""

    # Check ports are available
    for port in 8000 3000; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ Port $port is already in use"
            echo "   Run: just dev-local-stop"
            exit 1
        fi
    done

    # Start PostgreSQL if not running
    if ! docker compose -f docker-compose.deps.yml ps postgres | grep -q "Up"; then
        echo "📦 Starting PostgreSQL..."
        docker compose -f docker-compose.deps.yml up -d
    else
        echo "✅ PostgreSQL already running"
    fi

    # Get actual container name (handles both cinematch-postgres-1 and cinematch-main-postgres-1)
    PG_CONTAINER=$(docker compose -f docker-compose.deps.yml ps -q postgres 2>/dev/null | head -1)
    if [ -z "$PG_CONTAINER" ]; then
        echo "❌ Failed to get PostgreSQL container name"
        exit 1
    fi

    # Wait for PostgreSQL to be ready (max 30s)
    echo "⏳ Waiting for PostgreSQL..."
    for i in {1..60}; do
        if docker exec "$PG_CONTAINER" pg_isready -U cinematch >/dev/null 2>&1; then
            echo "✅ PostgreSQL ready"
            break
        fi
        if [ $i -eq 60 ]; then
            echo "❌ PostgreSQL failed to start"
            exit 1
        fi
        sleep 0.5
    done
    echo ""

    # Clear old logs
    rm -f /tmp/cinematch-backend.log /tmp/cinematch-frontend.log

    # Start backend in background
    echo "🐍 Starting backend..."
    cd backend && DATABASE_URL="postgresql+psycopg://cinematch:cinematch@localhost:5432/cinematch" uv run uvicorn app.main:app --reload --port 8000 > /tmp/cinematch-backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/cinematch-backend.pid

    # Start frontend in background
    echo "⚡ Starting frontend..."
    cd frontend && pnpm dev > /tmp/cinematch-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/cinematch-frontend.pid

    # Wait for backend to be ready (max 30s)
    echo "⏳ Waiting for backend..."
    for i in {1..60}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo "✅ Backend ready"
            break
        fi
        if [ $i -eq 60 ]; then
            echo "❌ Backend failed to start"
            echo "   Logs: just dev-local-logs"
            just dev-local-stop
            exit 1
        fi
        sleep 0.5
    done

    # Wait for frontend to be ready (max 30s)
    echo "⏳ Waiting for frontend..."
    for i in {1..60}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            echo "✅ Frontend ready"
            break
        fi
        if [ $i -eq 60 ]; then
            echo "❌ Frontend failed to start"
            echo "   Logs: just dev-local-logs"
            just dev-local-stop
            exit 1
        fi
        sleep 0.5
    done

    echo ""
    echo "🎉 All services ready!"
    echo ""
    echo "📊 Services:"
    echo "   Backend:  http://localhost:8000"
    echo "   Frontend: http://localhost:3000"
    echo ""
    echo "📝 Logs: just dev-local-logs"
    echo "🛑 Stop: just dev-local-stop"

# Stop local dev services
dev-local-stop:
    #!/usr/bin/env bash
    set +e
    echo "🛑 Stopping services..."

    # Kill by PID files if they exist
    if [ -f /tmp/cinematch-backend.pid ]; then
        kill $(cat /tmp/cinematch-backend.pid) 2>/dev/null
        rm -f /tmp/cinematch-backend.pid
        echo "   Backend stopped"
    fi
    if [ -f /tmp/cinematch-frontend.pid ]; then
        kill $(cat /tmp/cinematch-frontend.pid) 2>/dev/null
        rm -f /tmp/cinematch-frontend.pid
        echo "   Frontend stopped"
    fi

    # Kill any processes on the ports (backup cleanup)
    for port in 8000 3000 3001 3002 3003; do
        PID=$(lsof -ti :$port -sTCP:LISTEN 2>/dev/null)
        if [ -n "$PID" ]; then
            kill -9 $PID 2>/dev/null
        fi
    done

    docker compose -f docker-compose.deps.yml down 2>/dev/null
    echo "   PostgreSQL stopped"
    echo "✅ All services stopped"

# Show combined logs
dev-local-logs:
    #!/usr/bin/env bash
    if command -v tail &>/dev/null; then
        echo "📝 Press Ctrl+C to exit logs (services keep running)"
        echo "========================================== BACKEND =========================================="
        tail -n 20 /tmp/cinematch-backend.log 2>/dev/null || echo "No backend logs yet"
        echo ""
        echo "========================================== FRONTEND =========================================="
        tail -n 20 /tmp/cinematch-frontend.log 2>/dev/null || echo "No frontend logs yet"
        echo ""
        echo "========================================== FOLLOWING =========================================="
        tail -f /tmp/cinematch-backend.log /tmp/cinematch-frontend.log 2>/dev/null
    else
        echo "Backend logs:"
        cat /tmp/cinematch-backend.log 2>/dev/null || echo "No backend logs"
        echo ""
        echo "Frontend logs:"
        cat /tmp/cinematch-frontend.log 2>/dev/null || echo "No frontend logs"
    fi

# Check if dev services are ready
dev-local-status:
    #!/usr/bin/env bash
    echo "📊 Services status:"
    echo ""

    # PostgreSQL
    PG_CONTAINER=$(docker compose -f docker-compose.deps.yml ps -q postgres 2>/dev/null | head -1)
    if [ -n "$PG_CONTAINER" ] && docker exec "$PG_CONTAINER" pg_isready -U cinematch >/dev/null 2>&1; then
        echo "   ✅ PostgreSQL: localhost:5432 (container: $PG_CONTAINER)"
    else
        echo "   ❌ PostgreSQL: not running"
    fi

    # Backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "   ✅ Backend:    http://localhost:8000"
    else
        echo "   ❌ Backend:    not running"
    fi

    # Frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "   ✅ Frontend:   http://localhost:3000"
    else
        echo "   ❌ Frontend:   not running"
    fi

    echo ""
    echo "Commands:"
    echo "   Start:  just dev-local"
    echo "   Logs:   just dev-local-logs"
    echo "   Stop:   just dev-local-stop"

# Alias for backward compatibility
check-dev: dev-local-status

# Stop local dev services
dev-local-down:
    docker compose -f docker-compose.deps.yml down

# Legacy docker-based dev (slower, full containerization)
dev-docker:
    docker compose up --build

dev-docker-down:
    docker compose down

dev-logs:
    docker compose -f docker-compose.deps.yml logs -f

check:
    cd backend && just check
    cd frontend && just check

test:
    cd backend && just test

docker-build:
    docker compose build

# Backend shortcuts
backend-dev:
    cd backend && just dev

backend-test:
    cd backend && just test

backend-lint:
    cd backend && just lint

# Frontend shortcuts
frontend-dev:
    cd frontend && just dev

frontend-build:
    cd frontend && just build

frontend-lint:
    cd frontend && just lint

# Check if current user is admin or contributor
# Usage: just check-role
check-role:
    #!/usr/bin/env bash
    set -e
    USER=$(gh api user -q .login 2>/dev/null || echo "")
    if [ -z "$USER" ]; then
        echo "❌ Not authenticated with GitHub CLI"
        echo "   Run: gh auth login"
        exit 1
    fi

    # Check admin permission via API
    if gh api repos/umans-ai/cinematch/collaborators/$USER/permission -q .permission 2>/dev/null | grep -q "admin"; then
        echo "👤 Role: ADMIN (Umans AI team)"
        echo "   Workflow: Create items on main, push to main"
    else
        echo "👤 Role: CONTRIBUTOR (external)"
        echo "   Workflow: Create branch first, everything on feature branch"
        echo "   Note: You cannot push to main"
    fi

# Maintainer: Accept a contributor and optionally close their issue
# Usage: just accept USERNAME [ISSUE_NUMBER]
accept USERNAME ISSUE="":
    #!/usr/bin/env bash
    set -e
    echo "🔑 Adding @{{USERNAME}} as contributor..."
    gh api repos/umans-ai/cinematch/collaborators/{{USERNAME}} -X PUT -f permission=push
    echo "✅ @{{USERNAME}} invited with 'push' permission"
    if [ -n "{{ISSUE}}" ]; then
        echo "💬 Posting welcome comment on issue #{{ISSUE}}..."
        gh issue comment {{ISSUE}} --body "Welcome @{{USERNAME}}! 🎉\n\nYou've been granted **write** access. You can now:\n- Clone directly: \`git clone https://github.com/umans-ai/cinematch.git\`\n- Push branches: \`git push origin your-branch\`\n- Get preview deployments on every PR\n\nSee [CONTRIBUTING.md](../../blob/main/CONTRIBUTING.md) to get started."
        echo "🔒 Closing issue #{{ISSUE}}..."
        gh issue close {{ISSUE}} --reason completed
        echo "✅ Issue closed"
    fi
    echo ""
    echo "📧 @{{USERNAME}} will receive an email invitation to accept"
