dev:
    docker-compose up --build

dev-logs:
    docker-compose logs -f

dev-down:
    docker-compose down

check:
    cd backend && just check
    cd frontend && just check

test:
    cd backend && just test

docker-build:
    docker-compose build

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
