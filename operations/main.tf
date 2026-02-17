terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "umans-terraform-state"
    key            = "cinematch/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "cinematch"
      Environment = terraform.workspace
      ManagedBy   = "terraform"
    }
  }
}

locals {
  is_preview = terraform.workspace != "production"
  subdomain  = local.is_preview ? "demo-pr-${var.preview_number}" : "demo"
  domain     = "${local.subdomain}.cinematch.umans.ai"
}

# Data sources

data "aws_route53_zone" "umans" {
  name = "umans.ai"
}

data "aws_acm_certificate" "umans" {
  domain   = "*.umans.ai"
  statuses = ["ISSUED"]
}

# ECS Cluster
resource "aws_ecs_cluster" "cinematch" {
  name = "cinematch-${terraform.workspace}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "cinematch" {
  cluster_name = aws_ecs_cluster.cinematch.name

  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# VPC and Networking (reuse existing if available, or create minimal)

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Groups

resource "aws_security_group" "alb" {
  name        = "cinematch-alb-${terraform.workspace}"
  description = "ALB for CineMatch ${terraform.workspace}"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "cinematch-ecs-${terraform.workspace}"
  description = "ECS tasks for CineMatch ${terraform.workspace}"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol        = "tcp"
    from_port       = 8000
    to_port         = 8000
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    protocol        = "tcp"
    from_port       = 3000
    to_port         = 3000
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ALB

resource "aws_lb" "cinematch" {
  name            = "cinematch-${terraform.workspace}"
  internal        = false
  security_groups = [aws_security_group.alb.id]
  subnets         = data.aws_subnets.default.ids

  enable_deletion_protection = !local.is_preview
}

resource "aws_lb_target_group" "backend" {
  name        = "cinematch-backend-${terraform.workspace}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_target_group" "frontend" {
  name        = "cinematch-frontend-${terraform.workspace}"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.cinematch.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# Route53

resource "aws_route53_record" "cinematch" {
  zone_id = data.aws_route53_zone.umans.zone_id
  name    = local.domain
  type    = "A"

  alias {
    name                   = aws_lb.cinematch.dns_name
    zone_id                = aws_lb.cinematch.zone_id
    evaluate_target_health = true
  }
}

# ECR Repositories

resource "aws_ecr_repository" "backend" {
  name                 = "cinematch-backend"
  image_tag_mutability = "MUTABLE"

  force_delete = local.is_preview
}

resource "aws_ecr_repository" "frontend" {
  name                 = "cinematch-frontend"
  image_tag_mutability = "MUTABLE"

  force_delete = local.is_preview
}

# ECS Task Definitions

resource "aws_ecs_task_definition" "backend" {
  family                   = "cinematch-backend-${terraform.workspace}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "sqlite:///tmp/cinematch.db"
        },
        {
          name  = "CORS_ORIGINS"
          value = "https://${local.domain}"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "backend"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "frontend" {
  family                   = "cinematch-frontend-${terraform.workspace}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = "${aws_ecr_repository.frontend.repository_url}:${var.image_tag}"
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "NEXT_PUBLIC_API_URL"
          value = "https://${local.domain}/api"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.frontend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "frontend"
        }
      }
    }
  ])
}

# ECS Services

resource "aws_ecs_service" "backend" {
  name            = "backend"
  cluster         = aws_ecs_cluster.cinematch.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}

resource "aws_ecs_service" "frontend" {
  name            = "frontend"
  cluster         = aws_ecs_cluster.cinematch.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.http]

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}

# CloudWatch Logs

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/cinematch-backend-${terraform.workspace}"
  retention_in_days = local.is_preview ? 1 : 7
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/cinematch-frontend-${terraform.workspace}"
  retention_in_days = local.is_preview ? 1 : 7
}

# IAM Roles

resource "aws_iam_role" "ecs_execution" {
  name = "cinematch-ecs-execution-${terraform.workspace}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "cinematch-ecs-task-${terraform.workspace}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}
