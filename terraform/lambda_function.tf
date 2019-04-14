resource "aws_iam_role" "timber_log_forwarder" {
  name = "${var.name}-timber_log_forwarder"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "timber_log_forwarder" {
  description      = "Forwards CloudWatch logs to the Timber.io service"
  s3_bucket        = "packages.timber.io"
  s3_key           = "cloudwatch-logs-lambda-function/timber-cloudwatch-logs-lambda-function-latest.zip"
  function_name    = "${var.name}-timber_log_forwarder"
  role             = "${aws_iam_role.timber_log_forwarder.arn}"
  handler          = "main.lambda_handler"
  runtime          = "python3.7"
  memory_size      = 512
  timeout          = 31

  environment {
    variables = {
      TIMBER_SOURCE_ID = "${var.source_id}"
      TIMBER_API_KEY = "${var.api_key}"
    }
  }
}

resource "aws_cloudwatch_log_group" "timber_log_forwarder" {
  name              = "/aws/lambda/${aws_lambda_function.timber_log_forwarder.function_name}"
  retention_in_days = 14
}

resource "aws_iam_policy" "timber_log_forwarder_logging" {
  name        = "timber_log_forwarder_logging"
  path        = "/"
  description = "IAM policy for logging from the Timber AWS Lambda forwarder"
  policy      = "${data.aws_iam_policy_document.timber_log_forwarder_logging.json}"
}

data "aws_iam_policy_document" "timber_log_forwarder_logging" {
  statement {
    sid = "PutCloudLogs"

    effect = "${var.enable_logging == "true" ? "Allow" : "Deny"}"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.timber_log_forwarder.arn}",
    ]
  }
}

resource "aws_iam_role_policy_attachment" "timber_log_forwarder_logging" {
  role = "${aws_iam_role.timber_log_forwarder.name}"
  policy_arn = "${aws_iam_policy.timber_log_forwarder_logging.arn}"
}

data "aws_region" "current" {}

data "aws_cloudwatch_log_group" "log_groups" {
  count = "${length(var.log_group_names)}"
  name  = "${element(var.log_group_names, count.index)}"
}

resource "aws_lambda_permission" "allow_cloudwatch_execution" {
  count         = "${length(var.log_group_names)}"
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.timber_log_forwarder.function_name}"
  principal     = "logs.${data.aws_region.current.name}.amazonaws.com"
  source_arn    = "${element(data.aws_cloudwatch_log_group.log_groups.*.arn, count.index)}"
}
