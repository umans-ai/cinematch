# ECS Cluster
# Shared cluster for all CineMatch environments (staging, production, previews)
# Each environment uses workspaces to isolate services

resource "aws_ecs_cluster" "cinematch" {
  name = "cinematch"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "cinematch" {
  cluster_name = aws_ecs_cluster.cinematch.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}
