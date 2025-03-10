# data "archive_file" "generate_translation_zip" {
#   type        = "zip"
#   source_dir  = "${path.module}/src"
#   output_path = "${path.module}/src/generate_translation.zip"
# }

data "archive_file" "get_translation_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/src/get_translation.zip"
}
