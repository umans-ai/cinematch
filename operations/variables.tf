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

variable "preview_number" {
  description = "Preview environment number (for preview workspaces)"
  type        = string
  default     = ""
}
