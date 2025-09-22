output "jump_host_id" {
  description = "Jump host instance ID"
  value       = aws_instance.jump_host.id
}

output "jump_host_private_ip" {
  description = "Jump host private IP address"
  value       = aws_instance.jump_host.private_ip
}

output "nat_instance_id" {
  description = "NAT instance ID"
  value       = aws_instance.nat_instance.id
}

output "nat_instance_public_ip" {
  description = "NAT instance public IP address"
  value       = aws_instance.nat_instance.public_ip
}

output "nat_instance_private_ip" {
  description = "NAT instance private IP address"
  value       = aws_instance.nat_instance.private_ip
}

output "jump_host_security_group_id" {
  description = "Jump host security group ID"
  value       = aws_security_group.jump_host_sg.id
}

output "nat_instance_security_group_id" {
  description = "NAT instance security group ID"
  value       = aws_security_group.nat_instance_sg.id
}
