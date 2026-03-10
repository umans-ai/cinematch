# VPC and Networking
# Per-environment VPC (all environments use their own VPC)

locals {
  # For previews: generate unique network offset to avoid CIDR conflicts
  # random_id gives 0-255, we add 10 but must stay <= 255 for valid IP octet
  network_offset = local.use_foundation_vpc ? 1 : (random_id.network_offset[0].dec % 246) + 10
}

# New VPC for all environments
resource "aws_vpc" "cinematch" {
  count = local.use_foundation_vpc ? 0 : 1

  cidr_block           = "10.${local.network_offset}.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    # Note: VPC was created with -green suffix during migration
    Name = "cinematch-${terraform.workspace}-green"
  }
}

# VPC ID selector
locals {
  vpc_id = local.use_foundation_vpc ? data.terraform_remote_state.foundation.outputs.vpc_id : aws_vpc.cinematch[0].id
}

# Public subnets
resource "aws_subnet" "public" {
  count                   = local.use_foundation_vpc ? 0 : 2
  vpc_id                  = local.vpc_id
  cidr_block              = "10.${local.network_offset}.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "cinematch-${terraform.workspace}-public-${count.index + 1}"
  }
}

# Private subnets for RDS
resource "aws_subnet" "private" {
  count                   = local.use_foundation_vpc ? 0 : 2
  vpc_id                  = local.vpc_id
  cidr_block              = "10.${local.network_offset}.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "cinematch-${terraform.workspace}-private-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "cinematch" {
  count  = local.use_foundation_vpc ? 0 : 1
  vpc_id = local.vpc_id

  tags = {
    Name = "cinematch-${terraform.workspace}-igw"
  }
}

# Route table
resource "aws_route_table" "public" {
  count  = local.use_foundation_vpc ? 0 : 1
  vpc_id = local.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cinematch[0].id
  }

  tags = {
    Name = "cinematch-${terraform.workspace}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = local.use_foundation_vpc ? 0 : 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# Subnet ID selectors
locals {
  public_subnet_ids  = local.use_foundation_vpc ? data.terraform_remote_state.foundation.outputs.public_subnet_ids : aws_subnet.public[*].id
  private_subnet_ids = local.use_foundation_vpc ? [] : aws_subnet.private[*].id
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# Generate unique network offset per workspace
resource "random_id" "network_offset" {
  count = local.use_foundation_vpc ? 0 : 1

  byte_length = 1

  keepers = {
    workspace = terraform.workspace
  }
}
