# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

  - Added terraform module under `/terraform`
  - Do not encode API key since it is no longer required

## [2.0.2] - 2019-02-24

### Changed

  - Update README
  - Add RELEASING.md

## [2.0.1] - 2019-02-23

### Changed

  - Updated the logs endpoint from `/sources/:source_id` to `/sources/:source_id/frames`

## [2.0.0] - 2019-02-23

### Changed

  - Require a source ID parameter for log routing.

## [1.0.3] - 2019-01-23

### Changed

  - No functional changes. Documentation and CI was updated.

## [1.0.2] - 2018-01-12

### Changed

  - Updated the AWS SAM template to accept the `TIMBER_API_KEY` environment variable.

## [1.0.1] - 2017-08-26

### Fixed

  - Ensure that multiple CloudWatch lines are joined with a \n character.

## [1.0.0] - 2017-08-26

- Initial release


[Unreleased]: https://github.com/timberio/timber-cloudwatch-logs-lambda-function/compare/v1.0.3...HEAD
[1.0.3]: https://github.com/timberio/odin/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/timberio/odin/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/timberio/odin/compare/v1.0.0...v1.0.1
