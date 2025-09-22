# VPC Outputs
output "dat_vpc_id" {
  description = "DAT VPC ID"
  value       = module.vpc.dat_vpc_id
}

output "dat_vpc_cidr_block" {
  description = "DAT VPC CIDR block"
  value       = module.vpc.dat_vpc_cidr_block
}

# ALB Outputs
output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Application Load Balancer zone ID"
  value       = module.alb.alb_zone_id
}

output "target_group_arn" {
  description = "Target Group ARN"
  value       = module.alb.target_group_arn
}

# Subnet Outputs
output "dat_public_subnet_ids" {
  description = "DAT Public Subnet IDs"
  value       = [module.subnet.dat_public_a_id, module.subnet.dat_public_b_id]
}

output "dat_private_subnet_ids" {
  description = "DAT Private Subnet IDs"
  value       = [module.subnet.dat_private_a_id, module.subnet.dat_private_b_id]
}

# EC2 Outputs
output "jump_host_private_ip" {
  description = "Jump host private IP address"
  value       = module.ec2.jump_host_private_ip
}

output "nat_instance_public_ip" {
  description = "NAT instance public IP address"
  value       = module.ec2.nat_instance_public_ip
}

# S3 Outputs
output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.bucket_name
}
