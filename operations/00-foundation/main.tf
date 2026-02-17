terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "umans-terraform-state"
    key            = "cinematch/foundation/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "cinematch"
      Layer       = "foundation"
      ManagedBy   = "terraform"
    }
  }
}

# Get existing Route53 zone (from llm-gateway foundation - READ ONLY)
# This is the ONLY shared resource - DNS zone is managed at org level
data "aws_route53_zone" "umans" {
  name = "umans.ai"
}

# ACM Certificate for cinematch subdomains (ISOLATED from llm-gateway)
# Using a separate certificate to ensure complete isolation
resource "aws_acm_certificate" "cinematch" {
  domain_name               = "cinematch.umans.ai"
  subject_alternative_names = ["*.cinematch.umans.ai"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# DNS validation records
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

# Dedicated VPC for CineMatch (COMPLETE ISOLATION from llm-gateway)
resource "aws_vpc" "cinematch" {
  cidr_block           = "10.1.0.0/16"  # Different from llm-gateway (10.0.0.0/16)
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "cinematch-vpc"
  }
}

# Public subnets across 2 AZs
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.cinematch.id
  cidr_block              = "10.1.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "cinematch-public-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "cinematch" {
  vpc_id = aws_vpc.cinematch.id

  tags = {
    Name = "cinematch-igw"
  }
}

# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.cinematch.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cinematch.id
  }

  tags = {
    Name = "cinematch-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ECS Cluster (dedicated to cinematch)
resource "aws_ecs_cluster" "cinematch" {
  name = "cinematch"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "cinematch" {
  cluster_name = aws_ecs_cluster.cinematch.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# ECR Repositories
resource "aws_ecr_repository" "backend" {
  name                 = "cinematch-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true  # Allow deletion for cleanup
}

resource "aws_ecr_repository" "frontend" {
  name                 = "cinematch-frontend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}
