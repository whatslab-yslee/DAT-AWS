# DAT Private Subnet A (10.0.10.0/24)
resource "aws_subnet" "dat_private_a" {
  assign_ipv6_address_on_creation                = false
  cidr_block                                     = "10.0.10.0/24"
  enable_dns64                                   = false
  enable_lni_at_device_index                     = 0
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_native                                    = false
  map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch                        = false
  private_dns_hostname_type_on_launch            = "ip-name"
  vpc_id                                         = var.dat_vpc_id
  availability_zone                              = "${var.aws_region}a"

  tags = {
    Name = "DAT-private-A"
    Type = "Private"
  }
}

# DAT Private Subnet B (10.0.11.0/24)
resource "aws_subnet" "dat_private_b" {
  assign_ipv6_address_on_creation                = false
  cidr_block                                     = "10.0.11.0/24"
  enable_dns64                                   = false
  enable_lni_at_device_index                     = 0
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_native                                    = false
  map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch                        = false
  private_dns_hostname_type_on_launch            = "ip-name"
  vpc_id                                         = var.dat_vpc_id
  availability_zone                              = "${var.aws_region}b"

  tags = {
    Name = "DAT-private-B"
    Type = "Private"
  }
}

# DAT Public Subnet B (10.0.1.0/24)
resource "aws_subnet" "dat_public_b" {
  assign_ipv6_address_on_creation                = false
  cidr_block                                     = "10.0.1.0/24"
  enable_dns64                                   = false
  enable_lni_at_device_index                     = 0
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_native                                    = false
  map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch                        = false
  private_dns_hostname_type_on_launch            = "ip-name"
  vpc_id                                         = var.dat_vpc_id
  availability_zone                              = "${var.aws_region}b"

  tags = {
    Name = "DAT-public-B"
    Type = "Public"
  }
}

# DAT Public Subnet A (10.0.0.0/24)
resource "aws_subnet" "dat_public_a" {
  assign_ipv6_address_on_creation                = false
  cidr_block                                     = "10.0.0.0/24"
  enable_dns64                                   = false
  enable_lni_at_device_index                     = 0
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_native                                    = false
  map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch                        = false
  private_dns_hostname_type_on_launch            = "ip-name"
  vpc_id                                         = var.dat_vpc_id
  availability_zone                              = "${var.aws_region}a"

  tags = {
    Name = "DAT-public-A"
    Type = "Public"
  }
}