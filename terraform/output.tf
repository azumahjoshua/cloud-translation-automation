output "input_bucket" {
  value = aws_s3_bucket.input_bucket.id
}

output "output_bucket" {
  value = aws_s3_bucket.output_bucket.id
}

output "dynamodb_table" {
  value = aws_dynamodb_table.translations.name
}

# output "generate_lambda_arn" {
#   value = aws_lambda_function.generate_translation_lambda.arn
# }

output "get_lambda_arn" {
  value = aws_lambda_function.get_translation_lambda.arn
}

output "api_gateway_endpoint" {
  value = aws_api_gateway_stage.dev.invoke_url
}

