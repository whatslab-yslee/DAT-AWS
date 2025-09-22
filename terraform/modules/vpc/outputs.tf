output "dat_vpc_id" {
  description = "DAT VPC ID"
  value       = aws_vpc.dat_vpc.id
}

output "dat_vpc_cidr_block" {
  description = "DAT VPC CIDR block"
  value       = aws_vpc.dat_vpc.cidr_block
}

output "dat_igw_id" {
  description = "DAT Internet Gateway ID"
  value       = aws_internet_gateway.dat_igw.id
}
