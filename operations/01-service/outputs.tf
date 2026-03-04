output "url" {
  description = "Application URL"
  value       = "https://${aws_route53_record.cinematch.name}"
}

output "alb_dns" {
  description = "ALB DNS name"
  value       = aws_lb.cinematch.dns_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = local.vpc_id
}

output "db_endpoint" {
  description = "RDS endpoint (null for production/SQLite)"
  value       = length(aws_db_instance.cinematch) > 0 ? aws_db_instance.cinematch[0].endpoint : null
}

output "db_name" {
  description = "RDS database name (null for production/SQLite)"
  value       = length(aws_db_instance.cinematch) > 0 ? aws_db_instance.cinematch[0].db_name : null
}
