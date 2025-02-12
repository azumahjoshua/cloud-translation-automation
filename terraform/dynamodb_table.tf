# DynamoDB Table for Translations Cache
resource "aws_dynamodb_table" "translations" {
  name         = "TranslationsCache"
  billing_mode = "PAY_PER_REQUEST" # On-demand scaling
  hash_key     = "hash"

  attribute {
    name = "hash"
    type = "S" # String type for storing hash keys
  }

  ttl {
    attribute_name = "expiration_time"
    enabled        = true
  }

  tags = {
    Name        = "TranslationsCache"
    Environment = "Dev"
  }
}
