terraform {
  backend "s3" {
    bucket = "terraform-bucket-20250207"
    key    = "terraform/state.tfstate"
    region = "us-east-1"
  }
}
