# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Prevent application crash when the calculations database is missing.
- Implement sorting in search results and works by entity.
- Generate URLs for external entity links.
- Enable Docker deployment across different environments with Makefile commands.
- Integrate WSGI for production deployment.
- Add `mypy` for static type checking.
- Introduce `black` and `autoflake` as code formatting tools.
- Set up GitHub Actions for code style and static analysis testing.
- Improve error handling with detailed messages and exceptions.
- Add response tests for all endpoints.
- Define and use code constants across the project.
- Add endpoints for new entity types: other works, patents, and projects.
- Add changelog.
- Add sentry implementation for error reporting.

### Fixed
- Resolved incorrect data in the co-authorship world map.
- Fixed the broken co-authorship network functionality.
- Corrected Scimago quartile calculation by using the work's publication date in metadata.
- Fixed broken API documentation generation (Apidoc).
- Removed duplicate DOI data entries.
- Corrected sorting by publication year when the year is missing.
- Fixed issues with the Experts API.
- Improved database queries to retrieve accurate data for plots.

### Changed
- Refactored infrastructure files to support a more robust layered architecture.
- Updated the CSV file generation process.

### Removed
- Removed `odmantic` as the ODM (Object Document Mapper).
- Deprecated the `info` section in entity metadata.
- Removed entity metadata protocols.
- Consolidated different API versions into a single version.
