output "url" {
  description = "Application URL"
  value       = "https://${aws_route53_record.cinematch.name}"
}

output "alb_dns" {
  description = "ALB DNS name"
  value       = aws_lb.cinematch.dns_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.cinematch.address
}

output "database_url" {
  description = "Database connection URL (sensitive)"
  value       = local.database_url
  sensitive   = true
}
