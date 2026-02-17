# ECS Cluster
# Per-environment cluster (production, pr-123 each have their own)

resource "aws_ecs_cluster" "cinematch" {
  name = "cinematch-${terraform.workspace}"

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
