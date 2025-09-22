output "dat_main_route_table_id" {
  description = "DAT Main Route Table ID"
  value       = aws_route_table.dat_main_rt.id
}

output "dat_public_route_table_id" {
  description = "DAT Public Route Table ID"
  value       = aws_route_table.dat_public_rt.id
}

output "dat_private_route_table_id" {
  description = "DAT Private Route Table ID"
  value       = aws_route_table.dat_private_rt.id
}
