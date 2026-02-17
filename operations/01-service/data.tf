# Data Sources

# Reference to foundation layer outputs
data "terraform_remote_state" "foundation" {
  backend = "s3"
  config = {
    bucket = "umans-terraform-state"
    key    = "cinematch/foundation/terraform.tfstate"
    region = "eu-west-1"
  }
}

locals {
  is_production = terraform.workspace == "production"
}
