# Claude Instructions for pygenfsm

This document contains specific instructions for Claude when working on the pygenfsm project.

## Project Overview

pygenfsm is a minimal, clean, typed and synchronous FSM (Finite State Machine) implementation inspired by Erlang's gen_fsm.

## Development Workflow

### Quality Checks

**IMPORTANT**: Always run the following command at the end of any development task to ensure code quality:

```bash
uv run ruff format . && uv run ruff check . && uv run pyright . && uv run pytest
```

This command will:
1. Format code with ruff
2. Run linting checks with ruff
3. Run type checking with pyright
4. Run all tests with pytest

All checks must pass before considering a task complete.

### Code Style

- Use type hints everywhere
- Follow the existing code patterns
- Keep the implementation minimal and clean
- Ensure all examples demonstrate best practices

### Testing

- Add tests for any new functionality
- Ensure tests are properly typed
- Use pytest for all testing
- Maintain high code coverage (aim for >95%)

### Examples

When creating examples:
- Use type aliases for cleaner code (e.g., `LightFSM = FSM[LightState, LightEvent, LightData]`)
- Demonstrate both simple (enum) and complex (dataclass) event types
- Include docstrings explaining the example's purpose
- Make examples self-contained and runnable