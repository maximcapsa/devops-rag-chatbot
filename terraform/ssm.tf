# API keys are stored as encrypted SecureString parameters and fetched by the
# instance at deploy time — they never appear in user_data or the image.
resource "aws_ssm_parameter" "groq" {
  name  = "/${var.project_name}/groq_api_key"
  type  = "SecureString"
  value = var.groq_api_key
}

resource "aws_ssm_parameter" "voyage" {
  name  = "/${var.project_name}/voyage_api_key"
  type  = "SecureString"
  value = var.voyage_api_key
}
