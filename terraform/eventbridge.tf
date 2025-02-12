# resource "aws_cloudwatch_event_bus" "translation_event_bus" {
#   name = "TranslationEventBus"
# }

# resource "aws_cloudwatch_event_rule" "apigateway_event_rule" {
#   name          = "APIGatewayToEventBridgeRule"
#   description   = "Capture API Gateway events for translation"
#   event_bus_name = aws_cloudwatch_event_bus.translation_event_bus.name
#   event_pattern = jsonencode({
#     source      = ["api.gateway"]
#     detail-type = ["API Gateway Execution"]
#   })
# }

# resource "aws_cloudwatch_event_target" "eventbridge_to_lambda" {
#   rule          = aws_cloudwatch_event_rule.apigateway_event_rule.name
#   event_bus_name = aws_cloudwatch_event_bus.translation_event_bus.name
#   target_id     = "TranslationLambdaTarget"
#   arn           = aws_lambda_function.generate_translation_lambda.arn
# }
