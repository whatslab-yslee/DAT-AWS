variable "dat_vpc_id" {
  description = "DAT VPC ID"
  type        = string
}

variable "dat_vpc_cidr_block" {
  description = "DAT VPC CIDR block"
  type        = string
}

variable "dat_private_a_subnet_id" {
  description = "DAT Private Subnet A ID"
  type        = string
}

variable "dat_public_a_subnet_id" {
  description = "DAT Public Subnet A ID"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ami_id" {
  description = "AMI ID for jump host"
  type        = string
  default     = "ami-0c593c3690c32e925" # Amazon Linux 2
}

variable "nat_ami_id" {
  description = "AMI ID for NAT instance"
  type        = string
  default     = "ami-01ad0c7a4930f0e43" # NAT AMI
}

variable "iam_instance_profile" {
  description = "IAM instance profile for jump host"
  type        = string
  default     = "EC2-SSM-Jump-Role"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access instances"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
