# A small "prod" estate applied against LocalStack (a sandbox AWS): an existing S3 bucket, and a
# generated database password that lives only in state. No real cloud, no real credentials.

terraform {
  required_providers {
    aws    = { source = "hashicorp/aws" }
    random = { source = "hashicorp/random" }
  }
}

# LocalStack endpoint + dummy creds — never a real AWS account.
provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "us-east-1"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true
  endpoints {
    s3 = "http://localstack:4566"
  }
}

# The application log bucket.
resource "aws_s3_bucket" "app_logs" {
  bucket = "acme-app-logs"
  tags = merge({
    team = "platform"
    env  = "prod"
  }, local.inventory_tags)
}

# The database master password. Terraform marks its result sensitive; it lives only in state.
resource "random_password" "db_master" {
  length = 24
}
