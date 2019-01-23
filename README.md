# 🌲 Timber CloudWatch Logs Lambda Function

This AWS Lambda function enables you to stream your AWS CloudWatch logs to your Timber account.
It utilizes [log data subscriptions](http://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Subscriptions.html)
to achieve log delivery.

## Installation

Please consult the [Timber.io CloudWatch installation docs](https://timber.io/docs/platforms/aws-cloudwatch-logs/installation) for instructions.
You can also get account specific instructions immediately after creating an app within the
[Timber console](https://app.timber.io).

## Integrations

Timber will recognize popular events and formats, parsing them automatically to structure your logs.
For example, AWS lambda report events that log memory usage and execution timings. Timber will
automatically parse these messages giving you structured data to search and graph.

## Releasing

* Update CHANGELOG.md
* Create a git tag with the version prefixed with `v`
