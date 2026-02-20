# VPC and Networking
# Dedicated VPC for CineMatch (COMPLETE ISOLATION from other Umans AI projects)

resource "aws_vpc" "cinematch" {
  cidr_block           = "10.1.0.0/16"  # Distinct range from other internal infrastructure
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

data "aws_availability_zones" "available" {
  state = "available"
}
