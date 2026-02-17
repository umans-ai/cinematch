# Route53 DNS Records
# Per-environment DNS records

locals {
  subdomain = local.is_production ? "demo" : "demo-${terraform.workspace}"
  domain    = "${local.subdomain}.cinematch.umans.ai"
}

resource "aws_route53_record" "cinematch" {
  zone_id = data.terraform_remote_state.foundation.outputs.route53_zone_id
  name    = local.domain
  type    = "A"

  alias {
    name                   = aws_lb.cinematch.dns_name
    zone_id                = aws_lb.cinematch.zone_id
    evaluate_target_health = true
  }
}
