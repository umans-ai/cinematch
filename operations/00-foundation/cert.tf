# ACM Certificate
# SSL certificate for cinematch.umans.ai and *.cinematch.umans.ai
# Used by all environments (via subdomains)

resource "aws_acm_certificate" "cinematch" {
  domain_name               = "cinematch.umans.ai"
  subject_alternative_names = ["*.cinematch.umans.ai"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# DNS validation records in the shared umans.ai zone
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cinematch.domain_validation_options : dvo.domain_name => dvo
  }

  allow_overwrite = true
  zone_id         = data.aws_route53_zone.umans.zone_id
  name            = each.value.resource_record_name
  type            = each.value.resource_record_type
  records         = [each.value.resource_record_value]
  ttl             = 60
}

resource "aws_acm_certificate_validation" "cinematch" {
  certificate_arn         = aws_acm_certificate.cinematch.arn
  validation_record_fqdns = [for rec in aws_route53_record.cert_validation : rec.fqdn]
}

# Reference to the shared Route53 zone (org-level, READ-ONLY)
data "aws_route53_zone" "umans" {
  name = "umans.ai"
}
