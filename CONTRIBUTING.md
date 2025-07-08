# Contributing to pygenfsm

First off, thank you for considering contributing to pygenfsm! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and expected**
- **Include code samples and error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/pygenfsm
cd pygenfsm

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .
uv run pyright .
```

## Style Guide

- We use `ruff` for formatting and linting
- We use `pyright` for type checking
- All code must be properly typed
- Write descriptive commit messages
- Keep line length to 88 characters (ruff default)

## Testing

- Write tests for any new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage (>80%)
- Use `pytest` for all tests

## Documentation

- Update the README.md if needed
- Add docstrings to all public functions
- Include type hints for all parameters
- Update examples if API changes

Thank you for contributing! 🙏