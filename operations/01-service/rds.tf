# RDS PostgreSQL Database
# Managed PostgreSQL instance for CineMatch
# Note: RDS is only created for non-production workspaces (previews)
# Production uses SQLite until VPC migration is complete

# DB Subnet Group - only for previews (private subnets required)
resource "aws_db_subnet_group" "cinematch" {
  count = length(local.private_subnet_ids) > 0 ? 1 : 0

  name       = "cinematch-${terraform.workspace}"
  subnet_ids = local.private_subnet_ids

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}

# Security Group for RDS - only for previews
resource "aws_security_group" "rds" {
  count = length(local.private_subnet_ids) > 0 ? 1 : 0

  name        = "cinematch-rds-${terraform.workspace}"
  description = "RDS PostgreSQL for CineMatch ${terraform.workspace}"
  vpc_id      = local.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = 5432
    to_port         = 5432
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cinematch-rds-${terraform.workspace}"
  }
}

# Generate random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = false
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "cinematch" {
  count = length(local.private_subnet_ids) > 0 ? 1 : 0

  # Note: identifier stays as -green due to migration history
  # Changing it would force recreate (destroy+create) which loses data
  identifier     = "cinematch-${terraform.workspace}-green"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "cinematch"
  username = "cinematch"
  password = random_password.db_password.result

  db_subnet_group_name   = aws_db_subnet_group.cinematch[0].name
  vpc_security_group_ids = [aws_security_group.rds[0].id]

  publicly_accessible     = false
  skip_final_snapshot     = true
  deletion_protection     = false
  backup_retention_period = 1

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}
