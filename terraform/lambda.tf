# resource "aws_lambda_function" "generate_translation_lambda" {
#   function_name    = "GenerateTranslation"
#   runtime          = "python3.11"
#   role             = aws_iam_role.lambda_role.arn
#   handler          = "generate_translation.lambda_handler"
#   filename         = "${path.module}/src/generate_translation.zip"
#   source_code_hash = filebase64sha256("${path.module}/src/generate_translation.zip")

#   environment {
#     variables = {
#       TRANSLATION_CACHE_TABLE_NAME   = aws_dynamodb_table.translations.name
#       TRANSLATION_INPUT_BUCKET_NAME  = aws_s3_bucket.input_bucket.bucket
#       TRANSLATION_OUTPUT_BUCKET_NAME = aws_s3_bucket.output_bucket.bucket
#     }
#   }
# }

resource "aws_lambda_function" "get_translation_lambda" {
  function_name    = "GetTranslation"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_role.arn
  handler          = "get_translation.handler"
  filename         = "${path.module}/src/get_translation.zip"
  source_code_hash = filebase64sha256("${path.module}/src/get_translation.zip")

  environment {
    variables = {
      TRANSLATION_OUTPUT_BUCKET_NAME = aws_s3_bucket.output_bucket.bucket
      TRANSLATION_CACHE_TABLE_NAME   = aws_dynamodb_table.translations.name
      TRANSLATION_INPUT_BUCKET_NAME  = aws_s3_bucket.input_bucket.bucket
    }
  }
}


resource "aws_lambda_function" "upload_s3_lambda" {
  function_name    = "UploadS3"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_role.arn
  handler          = "upload_s3_lambda.lambda_handler"
  filename         = "${path.module}/src/upload_s3_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/src/upload_s3_lambda.zip")

  environment {
    variables = {
      TRANSLATION_INPUT_BUCKET_NAME = aws_s3_bucket.input_bucket.bucket
      TRANSLATION_LAMBDA_NAME       = aws_lambda_function.get_translation_lambda.function_name

    }
  }
}
