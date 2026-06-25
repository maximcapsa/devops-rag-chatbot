output "app_url" {
  description = "Public URL of the chatbot."
  value       = "http://${aws_instance.app.public_ip}"
}

output "instance_id" {
  description = "EC2 instance ID (used as the SSM RunCommand target)."
  value       = aws_instance.app.id
}

output "ecr_repository_url" {
  description = "ECR repository URL to push images to."
  value       = aws_ecr_repository.app.repository_url
}

output "log_group" {
  description = "CloudWatch log group for container logs."
  value       = aws_cloudwatch_log_group.app.name
}
