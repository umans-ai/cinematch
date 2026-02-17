# CloudWatch Logs
# Per-environment log groups

locals {
  is_production = terraform.workspace == "production"
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/cinematch-backend-${terraform.workspace}"
  retention_in_days = local.is_production ? 7 : 1
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/cinematch-frontend-${terraform.workspace}"
  retention_in_days = local.is_production ? 7 : 1
}
