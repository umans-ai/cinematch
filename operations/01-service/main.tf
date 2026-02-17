terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "umans-terraform-state"
    key            = "cinematch/service/terraform.tfstate"
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
      Layer       = "service"
      Environment = terraform.workspace
      ManagedBy   = "terraform"
    }
  }
}

locals {
  is_production = terraform.workspace == "production"
  subdomain     = local.is_production ? "demo" : "demo-${terraform.workspace}"
  domain        = "${local.subdomain}.cinematch.umans.ai"
}

# Data from foundation layer
data "terraform_remote_state" "foundation" {
  backend = "s3"
  config = {
    bucket = "umans-terraform-state"
    key    = "cinematch/foundation/terraform.tfstate"
    region = "eu-west-1"
  }
}

# Security Groups (ISOLATED)
resource "aws_security_group" "alb" {
  name        = "cinematch-alb-${terraform.workspace}"
  description = "ALB for CineMatch ${terraform.workspace}"
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id

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
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id

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

# Application Load Balancer
resource "aws_lb" "cinematch" {
  name               = "cinematch-${terraform.workspace}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.terraform_remote_state.foundation.outputs.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}

# Target Groups
resource "aws_lb_target_group" "backend" {
  name        = "cinematch-backend-${terraform.workspace}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id
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
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id
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

# ALB Listener - HTTP to HTTPS redirect or forward
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.cinematch.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# Route53 Record
data "aws_route53_zone" "umans" {
  name = "umans.ai"
}

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

# IAM Roles
resource "aws_iam_role" "ecs_execution" {
  name = "cinematch-ecs-exec-${terraform.workspace}"

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

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/cinematch-backend-${terraform.workspace}"
  retention_in_days = local.is_production ? 7 : 1
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/cinematch-frontend-${terraform.workspace}"
  retention_in_days = local.is_production ? 7 : 1
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "backend" {
  family                   = "cinematch-backend-${terraform.workspace}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = local.is_production ? "256" : "256"
  memory                   = local.is_production ? "512" : "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${data.terraform_remote_state.foundation.outputs.ecr_backend_url}:${var.image_tag}"
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
  cpu                      = local.is_production ? "256" : "256"
  memory                   = local.is_production ? "512" : "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = "${data.terraform_remote_state.foundation.outputs.ecr_frontend_url}:${var.image_tag}"
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
  cluster         = data.terraform_remote_state.foundation.outputs.ecs_cluster_id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.terraform_remote_state.foundation.outputs.public_subnet_ids
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
  cluster         = data.terraform_remote_state.foundation.outputs.ecs_cluster_id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.terraform_remote_state.foundation.outputs.public_subnet_ids
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
