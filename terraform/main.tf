# DAT Infrastructure - Main Configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }
  required_version = ">= 1.2"
}

provider "aws" {
  region = var.aws_region
}

# Local variables
locals {
  common_tags = {
    Project     = "DAT"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  tags = local.common_tags
}

# Subnet Module
module "subnet" {
  source = "./modules/subnet"
  
  aws_region      = var.aws_region
  dat_vpc_id      = module.vpc.dat_vpc_id
  
  depends_on = [module.vpc]
}

# ALB Module
module "alb" {
  source = "./modules/alb"
  
  dat_vpc_id              = module.vpc.dat_vpc_id
  dat_public_a_subnet_id  = module.subnet.dat_public_a_id
  dat_public_b_subnet_id  = module.subnet.dat_public_b_id
  certificate_arn         = var.certificate_arn
  
  depends_on = [module.vpc, module.subnet]
}

# Route Table Module
module "route_table" {
  source = "./modules/route_table"
  
  dat_vpc_id     = module.vpc.dat_vpc_id
  dat_igw_id     = module.vpc.dat_igw_id
  
  depends_on = [module.vpc]
}

# EC2 Module
module "ec2" {
  source = "./modules/ec2"
  
  dat_private_a_subnet_id = module.subnet.dat_private_a_id
  dat_public_a_subnet_id  = module.subnet.dat_public_a_id
  dat_vpc_id              = module.vpc.dat_vpc_id
  dat_vpc_cidr_block      = module.vpc.dat_vpc_cidr_block
  instance_type           = var.instance_type
  allowed_cidr_blocks     = var.allowed_cidr_blocks
  
  depends_on = [module.vpc, module.subnet]
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  tags = local.common_tags
}
