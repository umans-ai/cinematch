# CloudWatch Logs
# Per-environment log groups

resource "aws_cloudwatch_log_group" "backend" {
  # Note: Created with -green suffix during migration.
  # Log groups contain historical data; renaming loses it.
  name              = "/ecs/cinematch-backend-${terraform.workspace}-green"
  retention_in_days = local.is_production ? 7 : 1
}

resource "aws_cloudwatch_log_group" "frontend" {
  # Note: Created with -green suffix during migration.
  name              = "/ecs/cinematch-frontend-${terraform.workspace}-green"
  retention_in_days = local.is_production ? 7 : 1
}
