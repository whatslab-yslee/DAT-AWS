# Security Group for ALB
resource "aws_security_group" "alb_sg" {
  name_prefix = "dat-alb-"
  vpc_id      = var.dat_vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "DAT-ALB-SG"
  }
}

# Application Load Balancer
resource "aws_lb" "dat_alb" {
  name               = "whatslab-dat-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [var.dat_public_a_subnet_id, var.dat_public_b_subnet_id]

  enable_deletion_protection = false

  tags = {
    Name = "whatslab-dat-alb"
  }
}
