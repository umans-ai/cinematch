# Production Database Backup Instructions

## Prerequisites

Session Manager plugin required for ECS exec:
```bash
# macOS
brew install --cask session-manager-plugin

# Verify
session-manager-plugin
```

## Backup Commands

```bash
# 1. Get task ID
TASK_ARN=$(aws ecs list-tasks --region eu-west-1 --cluster cinematch-production --service-name backend --query "taskArns[0]" --output text)
TASK_ID=$(echo $TASK_ARN | cut -d'/' -f3)

# 2. Create backup in container
aws ecs execute-command \
  --region eu-west-1 \
  --cluster cinematch-production \
  --task $TASK_ID \
  --container backend \
  --interactive \
  --command "sh -c 'sqlite3 /app/data/cinematch.db .dump > /tmp/backup-$(date +%Y%m%d-%H%M%S).sql && ls -la /tmp/backup-*'"

# 3. Copy to S3 (from container, need AWS credentials in task)
# OR download via SSM and upload to S3
```

## Alternative: CI/CD Backup

Add to GitHub Actions workflow for automated backup before migration.
