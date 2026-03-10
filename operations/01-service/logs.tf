# CloudWatch Logs
# Per-environment log groups

resource "aws_cloudwatch_log_group" "backend" {
  # Keep -green suffix; log group is historical data
  name              = "/ecs/cinematch-backend-${terraform.workspace}-green"
  retention_in_days = local.is_production ? 7 : 1
}

resource "aws_cloudwatch_log_group" "frontend" {
  # Keep -green suffix; log group is historical data
  name              = "/ecs/cinematch-frontend-${terraform.workspace}-green"
  retention_in_days = local.is_production ? 7 : 1
}
