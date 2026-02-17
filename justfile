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
