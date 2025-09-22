# DAT VPC Subnets
output "dat_private_a_id" {
  description = "DAT Private Subnet A ID"
  value       = aws_subnet.dat_private_a.id
}

output "dat_private_b_id" {
  description = "DAT Private Subnet B ID"
  value       = aws_subnet.dat_private_b.id
}

output "dat_public_a_id" {
  description = "DAT Public Subnet A ID"
  value       = aws_subnet.dat_public_a.id
}

output "dat_public_b_id" {
  description = "DAT Public Subnet B ID"
  value       = aws_subnet.dat_public_b.id
}