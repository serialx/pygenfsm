# pygenfsm

A minimal, clean, typed and synchronous FSM (Finite State Machine) implementation inspired by Erlang's gen_fsm.

## Features

- **Type-safe**: Full typing support with generics
- **Minimal**: Clean, simple API with no dependencies
- **Pythonic**: Decorator-based state handler registration
- **Synchronous**: Simple, predictable execution model
- **Context-driven**: Each FSM instance can carry custom data
- **Dataclass events**: Events are dataclasses that can carry rich data payloads
- **Cloneable**: FSM instances can be cloned to create independent copies

## Requirements

- Python 3.11+

## Installation

```bash
pip install pygenfsm
```

## Quick Start

```python
from dataclasses import dataclass
from enum import Enum, auto
from pygenfsm import FSM

# Define states (enums) and events (dataclasses)
class LightState(Enum):
    OFF = auto()
    ON = auto()

@dataclass
class ToggleEvent:
    pass

# Optional: Define custom data
@dataclass
class LightContext:
    toggles: int = 0

# Type alias for cleaner code
LightFSM = FSM[LightState, ToggleEvent, LightContext]

# Create FSM instance
fsm = LightFSM(
    state=LightState.OFF,
    data=LightContext(),
)

# Register handlers using decorators
@fsm.on(LightState.OFF, ToggleEvent)
def turn_on(fsm: LightFSM, event: ToggleEvent):
    fsm.data.toggles += 1
    print("Light turned ON")
    return LightState.ON

@fsm.on(LightState.ON, ToggleEvent)
def turn_off(fsm: LightFSM, event: ToggleEvent):
    fsm.data.toggles += 1
    print("Light turned OFF")
    return LightState.OFF

# Use the FSM
fsm.send(ToggleEvent())  # Light turned ON
fsm.send(ToggleEvent())  # Light turned OFF
print(f"Total toggles: {fsm.data.toggles}")  # Total toggles: 2
```

## Complex Events with Context

Events can carry rich data payloads since they're dataclasses:

```python
from dataclasses import dataclass
from enum import Enum, auto
from pygenfsm import FSM

class DoorState(Enum):
    LOCKED = auto()
    UNLOCKED = auto()

@dataclass
class UnlockEvent:
    code: str
    user_id: int

@dataclass
class LockEvent:
    auto_lock: bool = False

# Union type for multiple event types
DoorEvent = UnlockEvent | LockEvent

@dataclass
class DoorContext:
    unlock_attempts: int = 0
    last_user: int = 0

# Type alias
DoorFSM = FSM[DoorState, DoorEvent, DoorContext]

door = DoorFSM(state=DoorState.LOCKED, data=DoorContext())

@door.on(DoorState.LOCKED, UnlockEvent)
def unlock_door(fsm: DoorFSM, event: UnlockEvent) -> DoorState:
    if event.code == "1234":
        fsm.data.last_user = event.user_id
        print(f"Door unlocked by user {event.user_id}")
        return DoorState.UNLOCKED
    else:
        fsm.data.unlock_attempts += 1
        print(f"Invalid code from user {event.user_id}")
        return DoorState.LOCKED

@door.on(DoorState.UNLOCKED, LockEvent)
def lock_door(fsm: DoorFSM, event: LockEvent) -> DoorState:
    print(f"Door locked (auto: {event.auto_lock})")
    return DoorState.LOCKED

# Use with rich event data
door.send(UnlockEvent(code="1234", user_id=42))
door.send(LockEvent(auto_lock=True))
```

## Cloning FSM Instances

You can create independent copies of an FSM using the `clone()` method:

```python
# Create an FSM
original = FSM(state=State.IDLE, context=Context(counter=0))

# ... register handlers ...

# Clone the FSM
cloned = original.clone()

# The clone has:
# - Same state as original
# - Deep copy of context (independent data)
# - Same handlers (shared behavior)

# Modifications to one don't affect the other
cloned.send(SomeEvent())  # Only affects cloned FSM
```

This is useful for:
- Creating multiple independent instances with the same behavior
- Saving/restoring FSM state
- Testing different scenarios from the same starting point

## Examples

Check out the `examples/` directory for more complex examples:

- `light_example.py` - Simple toggle switch
- `demo.py` - Traffic light and door lock examples
- `network_connection.py` - Complex events with data payloads
- `payment_processing.py` - Real-world payment flow with typed events

## Design Philosophy

**States are enums, Events are dataclasses**

- **States**: Use Python enums to represent the finite set of possible states
- **Events**: Use dataclasses to represent events, allowing them to carry rich data payloads
- **Context**: Use dataclasses for FSM instance data to maintain state between transitions

This design provides:
- **Type safety**: Full typing support with precise event types
- **Flexibility**: Events can carry any data needed for state transitions
- **Clarity**: Clear separation between states (what the FSM *is*) and events (what *happens* to the FSM)

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