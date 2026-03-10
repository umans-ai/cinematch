variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "create_new_vpc" {
  description = "Temporary: Create new VPC for production migration (blue-green deployment)"
  type        = bool
  default     = false
}
