output "url" {
  description = "Application URL"
  value       = "https://${aws_route53_record.cinematch.name}"
}

output "alb_dns" {
  description = "ALB DNS name"
  value       = aws_lb.cinematch.dns_name
}
