Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

[Unreleased](https://github.com/jshwi/readmetester/compare/v2.1.0...HEAD)
------------------------------------------------------------------------
### Fixed
- Prevents recursively executing self

[2.1.0](https://github.com/jshwi/readmetester/releases/tag/v2.1.0) - 2022-04-02
------------------------------------------------------------------------
### Added
- Warns when README contains no code blocks
- Adds linter for README
- Adds additional errors inheriting from `OutputDocumentError`
- Adds `--version` optional argument

### Changed
- Updates help

[2.0.0](https://github.com/jshwi/readmetester/releases/tag/v2.0.0) - 2022-03-26
------------------------------------------------------------------------
### Removed
- Removes collections from public API

[1.2.1](https://github.com/jshwi/readmetester/releases/tag/v1.2.1) - 2022-03-25
------------------------------------------------------------------------
### Fix
- Prevents error from being raised if pyproject.toml not in project

[1.2.0](https://github.com/jshwi/readmetester/releases/tag/v1.2.0) - 2022-03-24
------------------------------------------------------------------------
### Added
- Adds pyproject.toml configuration for style

[1.1.0](https://github.com/jshwi/readmetester/releases/tag/v1.1.0) - 2022-03-24
------------------------------------------------------------------------
### Added
- Allows line break to end code block
- Allows line breaks in code blocks for evaluated code
- Adds `__all__` to `readmetester.__init__`

[1.0.1](https://github.com/jshwi/readmetester/releases/tag/v1.0.1) - 2021-08-10
------------------------------------------------------------------------
### Security
- Upgraded dev packages

[1.0.0](https://github.com/jshwi/readmetester/releases/tag/v1.0.0) - 2021-03-16
------------------------------------------------------------------------
### Added
- Initial Release
