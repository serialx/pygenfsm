# pygenfsm

A minimal, clean, typed and async FSM (Finite State Machine) implementation inspired by Erlang's gen_fsm.

## Features

- **Type-safe**: Full typing support with generics
- **Minimal**: Clean, simple API with no dependencies
- **Pythonic**: Decorator-based state handler registration
- **Flexible**: Supports both sync and async handlers in the same FSM
- **Async-native**: Built for async/await with synchronous compatibility
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
import asyncio
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
    context=LightContext(),
)

# Register async handlers using decorators
@fsm.on(LightState.OFF, ToggleEvent)
async def turn_on(fsm: LightFSM, event: ToggleEvent):
    fsm.context.toggles += 1
    print("Light turned ON")
    return LightState.ON

@fsm.on(LightState.ON, ToggleEvent)
async def turn_off(fsm: LightFSM, event: ToggleEvent):
    fsm.context.toggles += 1
    print("Light turned OFF")
    return LightState.OFF

# Use the FSM
async def main():
    await fsm.send(ToggleEvent())  # Light turned ON
    await fsm.send(ToggleEvent())  # Light turned OFF
    print(f"Total toggles: {fsm.context.toggles}")  # Total toggles: 2

asyncio.run(main())
```

## Complex Events with Context

Events can carry rich data payloads since they're dataclasses:

```python
import asyncio
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

door = DoorFSM(state=DoorState.LOCKED, context=DoorContext())

@door.on(DoorState.LOCKED, UnlockEvent)
async def unlock_door(fsm: DoorFSM, event: UnlockEvent) -> DoorState:
    if event.code == "1234":
        fsm.context.last_user = event.user_id
        print(f"Door unlocked by user {event.user_id}")
        return DoorState.UNLOCKED
    else:
        fsm.context.unlock_attempts += 1
        print(f"Invalid code from user {event.user_id}")
        return DoorState.LOCKED

@door.on(DoorState.UNLOCKED, LockEvent)
async def lock_door(fsm: DoorFSM, event: LockEvent) -> DoorState:
    print(f"Door locked (auto: {event.auto_lock})")
    return DoorState.LOCKED

# Use with rich event data
async def main():
    await door.send(UnlockEvent(code="1234", user_id=42))
    await door.send(LockEvent(auto_lock=True))

asyncio.run(main())
```

## Late Context Injection with FSMBuilder

When your context contains objects that are created later in the application lifecycle (like database connections), use `FSMBuilder`:

```python
from pygenfsm import FSMBuilder

# Define your FSM builder without context
builder = FSMBuilder[State, Event, Context](initial_state=State.IDLE)

# Register async handlers on the builder
@builder.on(State.IDLE, StartEvent)
async def handle_start(fsm, event: StartEvent) -> State:
    # No need to check if context is None!
    await fsm.context.connection.send(event.data)
    return State.ACTIVE

# Later, when dependencies are available...
db_connection = create_database_connection()
context = Context(connection=db_connection)

# Build FSM instance with context
fsm = builder.build(context)

# Or create multiple instances with different contexts
fsm1 = builder.build(Context(connection=conn1))
fsm2 = builder.build(Context(connection=conn2))
```

This pattern is useful for:
- Dependency injection scenarios
- Creating FSM instances after application initialization
- Building multiple FSM instances with different contexts but same behavior

## Examples

Check out the `examples/` directory for more complex examples:

- `light_example.py` - Simple async toggle switch
- `demo.py` - Traffic light and door lock examples with async handlers
- `network_connection.py` - Complex events with data payloads
- `payment_processing.py` - Real-world payment flow with typed events
- `context_injection.py` - Using FSMBuilder for late context injection
- `context_replacement.py` - Replacing context in existing FSM instances
- `clone_example.py` - Cloning FSM instances for independent copies
- `mixed_handlers.py` - Mixing sync and async handlers in one FSM

## Mixed Sync/Async Handlers

pygenfsm supports both synchronous and asynchronous handlers in the same FSM:

```python
# Sync handler - for simple state transitions
@fsm.on(State.IDLE, StartEvent)
def start_handler(fsm, event: StartEvent) -> State:
    # Simple synchronous processing
    return State.ACTIVE

# Async handler - for I/O or complex operations  
@fsm.on(State.ACTIVE, ProcessEvent)
async def process_handler(fsm, event: ProcessEvent) -> State:
    # Async I/O operations
    await some_async_operation()
    return State.DONE

# Both work seamlessly with await fsm.send()
async def main():
    await fsm.send(StartEvent())   # Sync handler
    await fsm.send(ProcessEvent()) # Async handler
```

## Synchronous Usage

For purely synchronous code, use `send_sync()` with sync handlers:

```python
# Only works with sync handlers
fsm.send_sync(StartEvent())
# Raises RuntimeError if handler is async
```

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