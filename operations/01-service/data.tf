# Data Sources

# Reference to foundation layer outputs (ECR, Route53, ACM only)
data "terraform_remote_state" "foundation" {
  backend = "s3"
  config = {
    bucket = "umans-terraform-state"
    key    = "cinematch/foundation/terraform.tfstate"
    region = "eu-west-1"
  }
}

# Data source for Route53 zone
data "aws_route53_zone" "umans" {
  name         = "umans.ai"
  private_zone = false
}

locals {
  is_production = terraform.workspace == "production"
}
