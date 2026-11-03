resource "aws_s3_bucket" "archive" {
  bucket = "acme-archive"

  tags = {
    team = "platform"
    tier = "cold"
  }
}
