# pygenfsm

A minimal, clean, typed and synchronous FSM (Finite State Machine) implementation inspired by Erlang's gen_fsm.

## Features

- **Type-safe**: Full typing support with generics
- **Minimal**: Clean, simple API with no dependencies
- **Pythonic**: Decorator-based state handler registration
- **Synchronous**: Simple, predictable execution model
- **Data-driven**: Each FSM instance can carry custom data

## Installation

```bash
pip install pygenfsm
```

## Quick Start

```python
from dataclasses import dataclass
from enum import Enum, auto
from pygenfsm import FSM

# Define states and events
class LightState(Enum):
    OFF = auto()
    ON = auto()

class LightEvent(Enum):
    TOGGLE = auto()

# Optional: Define custom data
@dataclass
class LightData:
    toggles: int = 0

# Create FSM instance
fsm = FSM[LightState, LightEvent, LightData](
    state=LightState.OFF,
    data=LightData(),
)

# Register handlers using decorators
@fsm.on(LightState.OFF, LightEvent.TOGGLE)
def turn_on(fsm, evt):
    fsm.data.toggles += 1
    print("Light turned ON")
    return LightState.ON

@fsm.on(LightState.ON, LightEvent.TOGGLE)
def turn_off(fsm, evt):
    fsm.data.toggles += 1
    print("Light turned OFF")
    return LightState.OFF

# Use the FSM
fsm.send(LightEvent.TOGGLE)  # Light turned ON
fsm.send(LightEvent.TOGGLE)  # Light turned OFF
print(f"Total toggles: {fsm.data.toggles}")  # Total toggles: 2
```

## Examples

Check out the `examples/` directory for more complex examples:

- `light_example.py` - Simple toggle switch
- `demo.py` - Traffic light and door lock examples

## Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run type checking
uv run pyright

# Run linter and formatter
uv run ruff check --fix
uv run ruff format

# Install pre-commit hooks
uv run pre-commit install

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```

## License

MIT License - see LICENSE file for details.