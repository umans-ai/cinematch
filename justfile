# Local dev: fast feedback loop with PostgreSQL in Docker, code running locally
dev-local:
    #!/usr/bin/env bash
    set -e
    echo "🚀 Starting local dev environment..."
    echo ""

    # Start PostgreSQL if not running
    if ! docker compose -f docker-compose.deps.yml ps | grep -q "Up"; then
        echo "📦 Starting PostgreSQL..."
        docker compose -f docker-compose.deps.yml up -d
        sleep 2
    else
        echo "✅ PostgreSQL already running"
    fi

    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL..."
    until docker exec cinematch-postgres-1 pg_isready -U cinematch > /dev/null 2>&1; do
        sleep 0.5
    done
    echo "✅ PostgreSQL ready"
    echo ""

    # Start backend in background
    echo "🐍 Starting backend..."
    cd backend && DATABASE_URL="postgresql+psycopg://cinematch:cinematch@127.0.0.1:5432/cinematch" uv run uvicorn app.main:app --reload --port 8000 > /tmp/cinematch-backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/cinematch-backend.pid

    # Start frontend in background
    echo "⚡ Starting frontend..."
    cd frontend && pnpm dev > /tmp/cinematch-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/cinematch-frontend.pid

    # Wait for services to be ready
    echo "⏳ Waiting for services..."
    sleep 3

    # Show status
    echo ""
    echo "📊 Services:"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Backend:  http://localhost:8000"
    else
        echo "   ❌ Backend failed to start (see /tmp/cinematch-backend.log)"
    fi
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✅ Frontend: http://localhost:3000"
    else
        echo "   ❌ Frontend failed to start (see /tmp/cinematch-frontend.log)"
    fi
    echo ""
    echo "🧪 Ready for Playwright!"
    echo ""
    echo "📝 Logs:"
    echo "   tail -f /tmp/cinematch-backend.log"
    echo "   tail -f /tmp/cinematch-frontend.log"
    echo ""
    echo "🛑 Stop: just dev-local-stop"

# Stop local dev services
dev-local-stop:
    #!/usr/bin/env bash
    if [ -f /tmp/cinematch-backend.pid ]; then
        kill $(cat /tmp/cinematch-backend.pid) 2>/dev/null || true
        rm /tmp/cinematch-backend.pid
        echo "🛑 Backend stopped"
    fi
    if [ -f /tmp/cinematch-frontend.pid ]; then
        kill $(cat /tmp/cinematch-frontend.pid) 2>/dev/null || true
        rm /tmp/cinematch-frontend.pid
        echo "🛑 Frontend stopped"
    fi
    docker compose -f docker-compose.deps.yml down
    echo "🛑 PostgreSQL stopped"

# Check if dev services are ready
check-dev:
    #!/usr/bin/env bash
    set -e
    echo "🔍 Checking dev environment..."
    echo ""

    # Check PostgreSQL (using docker exec since pg_isready may not be installed locally)
    if docker exec cinematch-postgres-1 pg_isready -U cinematch >/dev/null 2>&1; then
        echo "✅ PostgreSQL: localhost:5432"
    else
        echo "❌ PostgreSQL: not ready (run: just dev-local)"
        exit 1
    fi

    # Check Backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend:    http://localhost:8000"
    else
        echo "❌ Backend:    not ready (cd backend && just dev-local)"
        exit 1
    fi

    # Check Frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend:   http://localhost:3000"
    else
        echo "❌ Frontend:   not ready (cd frontend && just dev)"
        exit 1
    fi

    echo ""
    echo "🎉 All services ready! Test with Playwright:"
    echo "   npx playwright test"

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
