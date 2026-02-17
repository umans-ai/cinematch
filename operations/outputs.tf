output "url" {
  description = "Application URL"
  value       = "https://${aws_route53_record.cinematch.name}"
}

output "alb_dns" {
  description = "ALB DNS name"
  value       = aws_lb.cinematch.dns_name
}

output "ecr_backend" {
  description = "Backend ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend" {
  description = "Frontend ECR repository URL"
  value       = aws_ecr_repository.frontend.repository_url
}
