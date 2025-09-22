# Security Group for Jump Host
resource "aws_security_group" "jump_host_sg" {
  name_prefix = "dat-jump-host-"
  vpc_id      = var.dat_vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "DAT-Jump-Host-SG"
  }
}

# Jump Host Instance
resource "aws_instance" "jump_host" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.dat_private_a_subnet_id
  vpc_security_group_ids = [aws_security_group.jump_host_sg.id]
  private_ip             = "10.0.10.69"
  source_dest_check      = false

  iam_instance_profile = var.iam_instance_profile

  root_block_device {
    delete_on_termination = true
    encrypted             = false
    volume_size           = 8
    volume_type           = "gp3"
  }

  tags = {
    Name = "dat-ssm-jump-host"
  }
}

# Security Group for NAT Instance
resource "aws_security_group" "nat_instance_sg" {
  name_prefix = "dat-nat-instance-"
  vpc_id      = var.dat_vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.dat_vpc_cidr_block]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.dat_vpc_cidr_block]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "DAT-NAT-Instance-SG"
  }
}

# NAT Instance
resource "aws_instance" "nat_instance" {
  ami                         = var.nat_ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.dat_public_a_subnet_id
  vpc_security_group_ids      = [aws_security_group.nat_instance_sg.id]
  associate_public_ip_address = true
  private_ip                  = "10.0.0.14"
  source_dest_check           = false

  root_block_device {
    delete_on_termination = true
    encrypted             = false
    volume_size           = 8
    volume_type           = "standard"
  }

  tags = {
    Name = "dat-vpc-nat-instance"
  }
}
