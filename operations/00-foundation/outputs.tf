output "vpc_id" {
  description = "CineMatch VPC ID"
  value       = aws_vpc.cinematch.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "certificate_arn" {
  description = "ACM certificate ARN for cinematch.umans.ai"
  value       = aws_acm_certificate_validation.cinematch.certificate_arn
}

output "ecs_cluster_id" {
  description = "ECS Cluster ID"
  value       = aws_ecs_cluster.cinematch.id
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.cinematch.name
}

output "ecr_backend_url" {
  description = "Backend ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "Frontend ECR repository URL"
  value       = aws_ecr_repository.frontend.repository_url
}

output "route53_zone_id" {
  description = "Route53 zone ID (umans.ai)"
  value       = data.aws_route53_zone.umans.zone_id
}
