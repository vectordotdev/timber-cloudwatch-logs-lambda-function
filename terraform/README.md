# Timber AWS CloudWatch Lambda - Terraform Resources

This folder serves as a Terraform module that you can reference to easily setup Timber's CloudWatch Logs Lambda forwarding function.

## Installation

```
module "timber_log_forwarding" {
  source = "git::git@github.com:timberio/timber-cloudwatch-logs-lambda-function.git//terraform"

  log_group_names = [
    "aws/lambda/hello_world"
  ]

  # Obtain both of these at https://app.timber.io
  api_key = "YOUR_API_KEY"
  source_id = "YOUR_SPURCE_ID"
}
```

### Multiple Sources

Many Timber customers like to create an individual source for each CloudWatch log group they're forwarding. To accomplish this simple define multiple `module "timber_log_forwarding" { ... }` blocks with the appropriate `source_id`.