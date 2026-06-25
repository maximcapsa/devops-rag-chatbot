# Latest Amazon Linux 2023 AMI via the public SSM parameter.
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

locals {
  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    region        = var.aws_region
    ecr_repo_url  = aws_ecr_repository.app.repository_url
    groq_param    = aws_ssm_parameter.groq.name
    voyage_param  = aws_ssm_parameter.voyage.name
    groq_model    = var.groq_model
    voyage_model  = var.voyage_model
    log_group     = aws_cloudwatch_log_group.app.name
    cw_config_ssm = aws_ssm_parameter.cw_agent_config.name
  })
}

resource "aws_instance" "app" {
  ami                         = data.aws_ssm_parameter.al2023.value
  instance_type               = var.instance_type
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  vpc_security_group_ids      = [aws_security_group.app.id]
  subnet_id                   = data.aws_subnets.default.ids[0]
  user_data                   = local.user_data
  user_data_replace_on_change = true

  metadata_options {
    http_tokens = "required" # enforce IMDSv2
  }

  root_block_device {
    volume_size = 20 # within the 30 GB Free Tier EBS allowance
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "${var.project_name}-app"
    App  = var.project_name # used by the deploy workflow to target SSM commands
  }
}
