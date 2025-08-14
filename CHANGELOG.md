# Changelog

All notable changes to pygenfsm will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2025-08-14

### Added
- Added `py.typed` marker file for PEP 561 compliance
- Full type checking support for library users with pyright, mypy, and other type checkers

## [1.0.0] - 2025-08-14

### Added
- Automated release workflow via GitHub Actions
- Comprehensive release documentation (RELEASE.md)
- GitHub Actions workflow for automated PyPI publishing
- Support for alpha/beta/RC pre-releases

### Changed
- Production-ready stable release
- Enhanced CI/CD pipeline with automated testing and publishing
- Improved package verification in CI workflow

### Fixed
- GitHub Actions workflow checkout configuration for tag releases
- Package verification in CI environment with proper venv usage

## [0.1.0] - 2025-01-14

### Added
- Initial release of pygenfsm
- Core FSM class with generic typing support for states, events, and context
- Decorator-based handler registration with `@fsm.on(state, event_type)`
- Support for both synchronous and asynchronous event handlers
- FSMBuilder for late context injection pattern
- Clone functionality for creating independent FSM copies
- Context replacement capability
- Full type safety with Python generics
- Support for Union event types
- Comprehensive test suite with 83% coverage
- Examples demonstrating various use cases:
  - Light switch FSM
  - Network connection with retry logic
  - Payment processing workflow
  - Context injection patterns
  - Mixed sync/async handlers

### Features
- Zero dependencies
- Python 3.11+ support
- Type-safe with full pyright strict mode compliance
- Async-native design
- Clean, minimal API surface
- Erlang gen_fsm inspired design

[Unreleased]: https://github.com/serialx/pygenfsm/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/serialx/pygenfsm/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/serialx/pygenfsm/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/serialx/pygenfsm/releases/tag/v0.1.0