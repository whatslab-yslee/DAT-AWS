output "alb_id" {
  description = "Application Load Balancer ID"
  value       = aws_lb.dat_alb.id
}

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = aws_lb.dat_alb.arn
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.dat_alb.dns_name
}

output "alb_zone_id" {
  description = "Application Load Balancer zone ID"
  value       = aws_lb.dat_alb.zone_id
}

output "target_group_id" {
  description = "Target Group ID"
  value       = aws_lb_target_group.dat_ecs_tg.id
}

output "target_group_arn" {
  description = "Target Group ARN"
  value       = aws_lb_target_group.dat_ecs_tg.arn
}

output "alb_security_group_id" {
  description = "ALB Security Group ID"
  value       = aws_security_group.alb_sg.id
}
