resource "aws_s3_bucket_policy" "tfer--whatslab-dat" {
  bucket = "whatslab-dat"
  policy = "{\"Statement\":[{\"Action\":[\"s3:ListBucket\",\"s3:GetObject\",\"s3:PutObject\"],\"Condition\":{\"StringEquals\":{\"aws:SourceVpce\":\"vpce-0b73c89c76ba05e41\"}},\"Effect\":\"Allow\",\"Principal\":\"*\",\"Resource\":[\"arn:aws:s3:::whatslab-dat\",\"arn:aws:s3:::whatslab-dat/*\"],\"Sid\":\"AllowS3AccessViaVPCE\"},{\"Action\":[\"s3:GetObject\",\"s3:PutObject\"],\"Condition\":{\"Bool\":{\"aws:SecureTransport\":\"true\"},\"StringEquals\":{\"s3:authType\":\"REST-QUERY-STRING\"}},\"Effect\":\"Allow\",\"Principal\":\"*\",\"Resource\":\"arn:aws:s3:::whatslab-dat/*\",\"Sid\":\"AllowPresignedURLAccess\"}],\"Version\":\"2012-10-17\"}"
}
