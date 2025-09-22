# DAT 프로젝트 전용 VPC
resource "aws_vpc" "dat_vpc" {
  assign_generated_ipv6_cidr_block     = false
  cidr_block                           = "10.0.0.0/16"
  enable_dns_hostnames                 = true
  enable_dns_support                   = true
  enable_network_address_usage_metrics = false
  instance_tenancy                     = "default"
  ipv6_netmask_length                  = 0

  tags = merge(var.tags, {
    Name = "DAT-vpc"
  })
}

# Internet Gateway for DAT VPC
resource "aws_internet_gateway" "dat_igw" {
  vpc_id = aws_vpc.dat_vpc.id

  tags = merge(var.tags, {
    Name = "DAT-IGW"
  })
}
