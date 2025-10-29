resource "aws_s3_bucket" "receipts" {
  bucket = "receipts-bucket"
  force_destroy = true
}