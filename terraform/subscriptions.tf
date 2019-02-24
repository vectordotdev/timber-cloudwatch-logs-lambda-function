resource "aws_cloudwatch_log_subscription_filter" "test_lambdafunction_logfilter" {
  count           = "${length(var.log_group_names)}"
  name            = "${element(var.log_group_names, count.index)} to Timber.io"
  role_arn        = "${aws_iam_role.timber_log_forwarder.arn}"
  log_group_name  = "${element(var.log_group_names, count.index)}"
  filter_pattern  = ""
  destination_arn = "${aws_lambda_function.timber_log_forwarder.arn}"
}