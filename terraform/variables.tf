variable "api_key" {
  type = "string"

  description = <<EOF
Your Timber API key. Create one at https://app.timber.io
EOF
}

variable "enable_logging" {
  type = "string"
  default = "false"

  description = <<EOF
Enable logging for the Timber lambda log forwarding function? Should be "true" or "false". If "true", a "aws/lambda/timber_log_forwarder" CloudWatch log group will be available.
EOF
}

variable "log_group_names" {
  type = "list"

  description = <<EOF
List of CloudWatch log group names to forward to Timber. Timber will create a subscription for each. An example of a log group name is "/aws/lambda/helloworld".
EOF
}

variable "source_id" {
  type = "string"

  description = <<EOF
Your Timber source ID. Create one at https://app.timber.io
EOF
}
