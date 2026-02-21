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

# Private subnets across 2 AZs (for RDS)
resource "aws_subnet" "private" {
  count                   = 2
  vpc_id                  = aws_vpc.cinematch.id
  cidr_block              = "10.1.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "cinematch-private-${count.index + 1}"
  }
}

# NAT Gateways for private subnets (needed for RDS to get updates, optional for MVP)
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"

  tags = {
    Name = "cinematch-nat-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "cinematch" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "cinematch-nat-${count.index + 1}"
  }
}

# Route table for private subnets
resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.cinematch.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.cinematch[count.index].id
  }

  tags = {
    Name = "cinematch-private-rt-${count.index + 1}"
  }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# DB Subnet Group
resource "aws_db_subnet_group" "cinematch" {
  name       = "cinematch-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "CineMatch DB Subnet Group"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
