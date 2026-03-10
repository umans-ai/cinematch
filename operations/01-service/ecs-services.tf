# ECS Services and Task Definitions
# Per-environment ECS services (frontend and backend)

# Database URL - SQLite for production (legacy), PostgreSQL for previews
locals {
  database_url = length(aws_db_instance.cinematch) > 0 ? (
    "postgresql://${aws_db_instance.cinematch[0].username}:${urlencode(random_password.db_password.result)}@${aws_db_instance.cinematch[0].endpoint}/${aws_db_instance.cinematch[0].db_name}"
  ) : "sqlite:///app/data/cinematch.db"
}

# Backend Task Definition
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
          value = local.database_url
        },
        {
          name  = "CORS_ORIGINS"
          value = "https://${local.domain}"
        },
        {
          name  = "RUN_MIGRATIONS"
          value = "true"
        }
      ]
      secrets = [
        {
          name      = "TMDB_API_KEY"
          valueFrom = data.aws_secretsmanager_secret.tmdb_api_key.arn
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

# Frontend Task Definition
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

# Backend ECS Service
resource "aws_ecs_service" "backend" {
  # Keep -green suffix to avoid service recreation
  name            = "backend-green"
  cluster         = aws_ecs_cluster.cinematch.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.public_subnet_ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.https]

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}

# Frontend ECS Service
resource "aws_ecs_service" "frontend" {
  # Keep -green suffix to avoid service recreation
  name            = "frontend-green"
  cluster         = aws_ecs_cluster.cinematch.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.public_subnet_ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.https]

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}
