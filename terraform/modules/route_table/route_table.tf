# DAT VPC Main Route Table
resource "aws_route_table" "dat_main_rt" {
  vpc_id = var.dat_vpc_id

  tags = {
    Name = "DAT-main-rt"
  }
}

# DAT VPC Public Route Table
resource "aws_route_table" "dat_public_rt" {
  vpc_id = var.dat_vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = var.dat_igw_id
  }

  tags = {
    Name = "DAT-public-rt"
  }
}

# DAT VPC Private Route Table (for NAT Gateway/Instance)
resource "aws_route_table" "dat_private_rt" {
  vpc_id = var.dat_vpc_id

  # Note: This route will be updated when NAT Gateway/Instance is created
  # route {
  #   cidr_block           = "0.0.0.0/0"
  #   network_interface_id = var.nat_instance_eni_id
  # }

  tags = {
    Name = "DAT-private-rt"
  }
}