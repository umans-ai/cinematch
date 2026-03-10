# Local values
locals {
  # All environments use per-environment VPC (migration complete)
  use_foundation_vpc = false

  # Domain configuration
  domain = terraform.workspace == "production" ? "demo.cinematch.umans.ai" : "demo-${terraform.workspace}.cinematch.umans.ai"

  # Common tags
  common_tags = {
    Environment = terraform.workspace
    Project     = "cinematch"
    ManagedBy   = "terraform"
  }
}
