# VPC and Networking (Per-Environment)
# Each workspace gets its own isolated VPC

resource "aws_vpc" "cinematch" {
  cidr_block           = "10.${local.network_offset}.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}

# Public subnets across 2 AZs
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.cinematch.id
  cidr_block              = "10.${local.network_offset}.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "cinematch-${terraform.workspace}-public-${count.index + 1}"
  }
}

# Private subnets across 2 AZs (for RDS)
resource "aws_subnet" "private" {
  count                   = 2
  vpc_id                  = aws_vpc.cinematch.id
  cidr_block              = "10.${local.network_offset}.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "cinematch-${terraform.workspace}-private-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "cinematch" {
  vpc_id = aws_vpc.cinematch.id

  tags = {
    Name = "cinematch-${terraform.workspace}-igw"
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
    Name = "cinematch-${terraform.workspace}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# Generate unique network offset per workspace to avoid CIDR conflicts
resource "random_id" "network_offset" {
  byte_length = 1

  keepers = {
    workspace = terraform.workspace
  }
}

locals {
  # Use workspace-specific offset, avoiding 1 (reserved for production legacy)
  network_offset = terraform.workspace == "production" ? 1 : random_id.network_offset.dec + 10
}
