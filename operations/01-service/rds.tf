# RDS PostgreSQL Database
# Managed PostgreSQL instance for CineMatch

# DB Subnet Group
resource "aws_db_subnet_group" "cinematch" {
  name       = "cinematch-${terraform.workspace}"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "cinematch-rds-${terraform.workspace}"
  description = "RDS PostgreSQL for CineMatch ${terraform.workspace}"
  vpc_id      = aws_vpc.cinematch.id

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
  identifier     = "cinematch-${terraform.workspace}"
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

  db_subnet_group_name   = aws_db_subnet_group.cinematch.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible    = false
  skip_final_snapshot    = !local.is_production
  deletion_protection    = local.is_production
  backup_retention_period = local.is_production ? 7 : 1

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}
