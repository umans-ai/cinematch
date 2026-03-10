# CloudWatch Logs
# Per-environment log groups

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/cinematch-backend-${terraform.workspace}${local.env_suffix}"
  retention_in_days = local.is_production ? 7 : 1
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/cinematch-frontend-${terraform.workspace}${local.env_suffix}"
  retention_in_days = local.is_production ? 7 : 1
}
