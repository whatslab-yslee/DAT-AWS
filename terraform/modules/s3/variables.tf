variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
  default     = "whatslab-dat"
}

variable "tags" {
  description = "Tags to apply to S3 bucket"
  type        = map(string)
  default     = {}
}
