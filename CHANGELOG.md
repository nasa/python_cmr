# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- [pull/27](https://github.com/nasa/python_cmr/pull/27) New feature to search by `readable_granlue_name` https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#g-granule-ur-or-producer-granule-id
### Fixed
- [pull/27](https://github.com/nasa/python_cmr/pull/27) Fixed bug with constructing the `options` sent to CMR which was causing filters to not get applied correctly.
- [pull/28](https://github.com/nasa/python_cmr/pull/28) Fixed bug where `KeyError` was thrown if search result contained 0 hits

## [0.9.0]
### Added
- [pull/17](https://github.com/nasa/python_cmr/pull/17) New feature that allows sort_keys to be passed into this Api up to the CMR. Used the valid sort_keys as of July 2023

### Changed
- Updated dependency versions  

## [0.8.0]
### Added
- [pull/15](https://github.com/nasa/python_cmr/pull/15): New feature added to filter by granules within the circle around lat/lon
- [pull/12](https://github.com/nasa/python_cmr/pull/12): Added environments to module level to simplify imports to `from cmr import CMR_UAT`
### Changed
- Changed token url to being tokens in authorization headers.
- Add in bearer token function for use of EDL bearer token in authorization headers.

## [0.7.0]
### Added
- New workflow that runs lint and test
- New function `Query.token` to add an auth token to the request sent to CMR
### Changed
- Now building with [poetry](https://python-poetry.org/)

## [0.6.0]
### Added
- New support for querying variables (UMM-V)
### Changed
- Can now import `ToolQuery` `ServiceQuery` `VariableQuery` straight from cmr module. (e.g. `from cmr import ToolQuery`)

## [0.5.0]
### Added
- New support for querying tools (UMM-T) and services (UMM-S)
- CodeQL Analysis on pushes and pull requests
### Changed
- Moved to github.com/nasa/python_cmr

## [Older]
- Prior releases of this software originated from https://github.com/jddeal/python-cmr/releases

[Unreleased]: https://github.com/nasa/python_cmr/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/nasa/python_cmr/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/nasa/python_cmr/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/nasa/python_cmr/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/nasa/python_cmr/compare/ef0f9e7d67ce99d342a568bd6a098c3462df16d2...v0.5.0
[Older]: https://github.com/jddeal/python-cmr/releases
