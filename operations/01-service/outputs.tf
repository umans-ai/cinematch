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
  value       = aws_vpc.cinematch.id
}

output "db_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.cinematch.endpoint
}

output "db_name" {
  description = "RDS database name"
  value       = aws_db_instance.cinematch.db_name
}
