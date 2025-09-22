output "bucket_id" {
  description = "S3 bucket ID"
  value       = aws_s3_bucket.dat_bucket.id
}

output "bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.dat_bucket.bucket
}

output "bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.dat_bucket.arn
}

output "bucket_domain_name" {
  description = "S3 bucket domain name"
  value       = aws_s3_bucket.dat_bucket.bucket_domain_name
}
