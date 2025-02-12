variable "aws_s3_bucket" {
  type    = string
  default = "banks3-terraform-bucket-20250207"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_account_id" {
  type    = string
  default = "913524920824"

}
variable "translation_input_bucket_name" {
  type    = string
  default = "translation-input-bucket-imjskz"
}

variable "translation_output_bucket_name" {
  type    = string
  default = "translation-output-bucket-imjskz"
}

variable "integration_response_parameters" {
  type = map(string)
  default = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}