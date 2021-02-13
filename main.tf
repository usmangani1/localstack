provider "aws" {
  region                      = "us-east-1"
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  s3_force_path_style         = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    ec2            = "http://localhost:4566"
  }
}

variable "subnet_cidrs" {
  type        = "list"
}

resource "aws_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    name = "some-vpc"
  }
}

output "vpc" {
  value = aws_vpc.vpc.tags
}

resource "aws_subnet" "subnets" {
  count = length(var.subnet_cidrs)
  vpc_id = aws_vpc.vpc.id
  cidr_block = element(var.subnet_cidrs, count.index)
  tags = {
    name = "some-subnet-${count.index}"
  }
}

output "subnets" {
  value = aws_subnet.subnets.*.tags
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    name = "some-internet-gateway"
  }
}

output "internet_gateway" {
  value = aws_internet_gateway.internet_gateway.tags
}

resource "aws_eip" "eip" {
  vpc                     = true
  depends_on              = ["aws_internet_gateway.internet_gateway"]
  count                   = length(var.subnet_cidrs)
  tags = {
    name = "some-eip-${count.index}"
  }
}

output "eips" {
  value = aws_eip.eip.*.tags
}

resource "aws_nat_gateway" "nat_gateway" {
  allocation_id           = aws_eip.eip.*.id[count.index]
  subnet_id               = element(flatten(aws_subnet.subnets.*.id), count.index)
  count                   = length(var.subnet_cidrs)
  tags = {
    name = "some-nat-gateway-${count.index}"
  }
}

output "nat_gateway" {
  value = aws_nat_gateway.nat_gateway.*.tags
}
