# import terraform AWS library
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# setup AWS credentials
provider "aws" {
	shared_config_files      = ["/home/coryg/.aws/config"]
	shared_credentials_files = ["/home/coryg/.aws/credentials"]
	profile                  = "default"
}

# create bucket for client data
resource "aws_s3_bucket" "clientbucket" {
	bucket = "clients-aerotract"
}

# create and assign ACL to client bucket
resource "aws_s3_bucket_acl" "clientacl" {
	bucket = aws_s3_bucket.clientbucket.id
	acl    = "private"
}

# create bucket for database
resource "aws_s3_bucket" "databasebucket" {
	bucket = "database-aerotract"
}

# create and assign ACL to database bucket
resource "aws_s3_bucket_acl" "databaseacl" {
	bucket = aws_s3_bucket.databasebucket.id
	acl    = "private"
}
