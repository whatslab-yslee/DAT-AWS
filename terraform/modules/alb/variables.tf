variable "dat_vpc_id" {
  description = "DAT VPC ID"
  type        = string
}

variable "dat_public_a_subnet_id" {
  description = "DAT Public Subnet A ID"
  type        = string
}

variable "dat_public_b_subnet_id" {
  description = "DAT Public Subnet B ID"
  type        = string
}

variable "certificate_arn" {
  description = "SSL Certificate ARN"
  type        = string
  default     = ""
}
