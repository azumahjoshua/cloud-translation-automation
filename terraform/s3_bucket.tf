resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_s3_bucket" "input_bucket" {
  bucket = "translation-input-bucket-${random_string.suffix.result}"
}

resource "aws_s3_bucket" "output_bucket" {
  bucket = "translation-output-bucket-${random_string.suffix.result}"
}

