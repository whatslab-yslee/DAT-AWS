resource "aws_lb_target_group" "dat_ecs_tg" {
  name     = "dat-ecs-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.dat_vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 5
    interval            = 60
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 30
    unhealthy_threshold = 2
  }

  tags = {
    Name = "dat-ecs-tg"
  }
}
