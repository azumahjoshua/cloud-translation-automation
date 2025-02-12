# Define IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "TranslationLambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy for Lambda Permissions (S3, DynamoDB, API Gateway, Logs)
resource "aws_iam_policy" "lambda_policy" {
  name        = "TranslationLambdaPolicy"
  description = "Policy allowing Lambda to access S3, DynamoDB, API Gateway, and logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # CloudWatch Logging Permissions
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      # S3 Permissions for Uploading and Retrieving Files
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.translation_input_bucket_name}/*",
          "arn:aws:s3:::${var.translation_input_bucket_name}",
          "arn:aws:s3:::${var.translation_output_bucket_name}",
          "arn:aws:s3:::${var.translation_output_bucket_name}/*"
        ]
      },
      # DynamoDB Permissions for Caching Translations
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.translations.arn
      },
      # API Gateway Invocation Permission
      {
        Effect = "Allow"
        Action = [
          "execute-api:Invoke"
        ]
        Resource = "arn:aws:execute-api:*:*:*"
      },
      # AWS Translate Full Access
      {
        Effect = "Allow"
        Action = [
          "translate:TranslateText"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach Policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Attach AWS-Managed Policies (if needed)
resource "aws_iam_role_policy_attachment" "lambda_logging" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_translate" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_translate" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/TranslateFullAccess"
}
