# RDS PostgreSQL Database
# Per-environment PostgreSQL instance for CineMatch

# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = false
}

# Store password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "cinematch-db-password-${terraform.workspace}"
  description             = "Password for CineMatch PostgreSQL database (${terraform.workspace})"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "cinematch" {
  identifier = "cinematch-${terraform.workspace}"

  engine         = "postgres"
  engine_version = "16.3"
  instance_class = local.is_production ? "db.t3.small" : "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "cinematch"
  username = "cinematch_admin"
  password = random_password.db_password.result

  db_subnet_group_name   = data.terraform_remote_state.foundation.outputs.db_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = local.is_production ? 7 : 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  skip_final_snapshot = !local.is_production
  final_snapshot_identifier = local.is_production ? "cinematch-${terraform.workspace}-final" : null

  deletion_protection = local.is_production

  performance_insights_enabled    = local.is_production
  performance_insights_retention_period = local.is_production ? 7 : 0

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Name        = "cinematch-${terraform.workspace}"
    Environment = terraform.workspace
  }
}

# Output the database URL for ECS
locals {
  db_host     = aws_db_instance.cinematch.address
  db_name     = aws_db_instance.cinematch.db_name
  db_user     = aws_db_instance.cinematch.username
  db_password = random_password.db_password.result
  database_url = "postgresql://${local.db_user}:${local.db_password}@${local.db_host}/${local.db_name}"
}
