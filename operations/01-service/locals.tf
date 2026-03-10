# Local values for blue-green deployment support
locals {
  # Environment suffix for blue-green deployment
  # When create_new_vpc=true, resources get "-green" suffix for parallel deployment
  env_suffix = var.create_new_vpc ? "-green" : ""

  # Use foundation VPC for production UNLESS migration mode is enabled
  # During migration: create_new_vpc=true forces new VPC creation for blue-green deployment
  use_foundation_vpc = terraform.workspace == "production" && !var.create_new_vpc

  # Domain configuration
  domain = terraform.workspace == "production" ? "demo.cinematch.umans.ai" : "demo-${terraform.workspace}.cinematch.umans.ai"

  # Environment flags
  is_production = terraform.workspace == "production"

  # Common tags
  common_tags = {
    Environment = terraform.workspace
    Project     = "cinematch"
    ManagedBy   = "terraform"
  }
}
