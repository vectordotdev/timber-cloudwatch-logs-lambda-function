resource "aws_cloudwatch_log_subscription_filter" "test_lambdafunction_logfilter" {
  count           = "${length(var.log_group_names)}"
  name            = "${element(var.log_group_names, count.index)} to Timber.io"
  log_group_name  = "${element(var.log_group_names, count.index)}"
  filter_pattern  = ""
  distribution    = "ByLogStream"
  destination_arn = "${aws_lambda_function.timber_log_forwarder.arn}"

  depends_on = ["aws_lambda_permission.allow_cloudwatch_execution"]
}
