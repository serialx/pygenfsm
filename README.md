# 🔄 pygenfsm

<div align="center">

[![PyPI version](https://badge.fury.io/py/pygenfsm.svg)](https://badge.fury.io/py/pygenfsm)
[![Python](https://img.shields.io/pypi/pyversions/pygenfsm.svg)](https://pypi.org/project/pygenfsm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: pyright](https://img.shields.io/badge/type%20checked-pyright-blue.svg)](https://github.com/microsoft/pyright)
[![Test Coverage](https://img.shields.io/badge/coverage-83%25-green.svg)](https://github.com/serialx/pygenfsm)

**A minimal, clean, typed and async-native FSM (Finite State Machine) implementation for Python, inspired by Erlang's gen_fsm**

[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Features](#-features) •
[Examples](#-examples) •
[API Reference](#-api-reference) •
[Contributing](#-contributing)

</div>

---

## 🎯 Why pygenfsm?

Building robust state machines in Python often involves:
- 🤯 Complex if/elif chains that grow unmaintainable
- 🐛 Implicit state that's hard to reason about
- 🔀 Scattered transition logic across your codebase
- ❌ No type safety for states and events
- 🚫 Mixing sync and async code awkwardly

**pygenfsm** solves these problems with a minimal, elegant API that leverages Python's type system and async capabilities.

## ✨ Features

<table>
<tr>
<td>

### 🎨 Clean API
```python
@fsm.on(State.IDLE, StartEvent)
def handle_start(fsm, event):
    return State.RUNNING
```

</td>
<td>

### 🔄 Async Native
```python
@fsm.on(State.RUNNING, DataEvent)
async def handle_data(fsm, event):
    await process_data(event.data)
    return State.DONE
```

</td>
</tr>
<tr>
<td>

### 🎯 Type Safe
```python
# Full typing with generics
FSM[StateEnum, EventType, ContextType]
```

</td>
<td>

### 🚀 Zero Dependencies
```bash
# Minimal and fast
pip install pygenfsm
```

</td>
</tr>
</table>

### Key Benefits

- **🔒 Type-safe**: Full typing support with generics for states, events, and context
- **🎭 Flexible**: Mix sync and async handlers in the same FSM
- **📦 Minimal**: Zero dependencies, clean API surface
- **🐍 Pythonic**: Decorator-based, intuitive design
- **🔄 Async-native**: Built for modern async Python
- **📊 Context-aware**: Carry data between transitions
- **🧬 Cloneable**: Fork FSM instances for testing scenarios
- **🏗️ Builder pattern**: Late context injection support

## 📦 Installation

```bash
# Using pip
pip install pygenfsm

# Using uv (recommended)
uv add pygenfsm

# Using poetry
poetry add pygenfsm
```

## 🚀 Quick Start

### Basic Example

```python
import asyncio
from dataclasses import dataclass
from enum import Enum, auto
from pygenfsm import FSM

# 1. Define states as an enum
class State(Enum):
    IDLE = auto()
    RUNNING = auto()
    DONE = auto()

# 2. Define events as dataclasses
@dataclass
class StartEvent:
    task_id: str

@dataclass
class CompleteEvent:
    result: str

# 3. Create FSM with initial state
fsm = FSM[State, StartEvent | CompleteEvent, None](
    state=State.IDLE,
    context=None,  # No context needed for simple FSM
)

# 4. Define handlers with decorators
@fsm.on(State.IDLE, StartEvent)
def start_handler(fsm, event: StartEvent) -> State:
    print(f"Starting task {event.task_id}")
    return State.RUNNING

@fsm.on(State.RUNNING, CompleteEvent)
def complete_handler(fsm, event: CompleteEvent) -> State:
    print(f"Task completed: {event.result}")
    return State.DONE

# 5. Run the FSM
async def main():
    await fsm.send(StartEvent(task_id="123"))
    await fsm.send(CompleteEvent(result="Success!"))
    print(f"Final state: {fsm.state}")

asyncio.run(main())
```

## 🎯 Core Concepts

### States, Events, and Context

pygenfsm is built on three core concepts:

| Concept | Purpose | Implementation |
|---------|---------|----------------|
| **States** | The finite set of states your system can be in | Python Enum |
| **Events** | Things that happen to trigger transitions | Dataclasses |
| **Context** | Data that persists across transitions | Any Python type |

### Handler Types

pygenfsm seamlessly supports both sync and async handlers:

```python
# Sync handler - for simple state transitions
@fsm.on(State.IDLE, SimpleEvent)
def sync_handler(fsm, event) -> State:
    # Fast, synchronous logic
    return State.NEXT

# Async handler - for I/O operations
@fsm.on(State.LOADING, DataEvent)
async def async_handler(fsm, event) -> State:
    # Async I/O, network calls, etc.
    data = await fetch_data(event.url)
    fsm.context.data = data
    return State.READY
```

## 📚 Examples

### Traffic Light System

```python
from enum import Enum, auto
from dataclasses import dataclass
from pygenfsm import FSM

class Color(Enum):
    RED = auto()
    YELLOW = auto()
    GREEN = auto()

@dataclass
class TimerEvent:
    """Timer expired event"""
    pass

@dataclass
class EmergencyEvent:
    """Emergency button pressed"""
    pass

# Create FSM
traffic_light = FSM[Color, TimerEvent | EmergencyEvent, None](
    state=Color.RED,
    context=None,
)

@traffic_light.on(Color.RED, TimerEvent)
def red_to_green(fsm, event) -> Color:
    print("🔴 → 🟢")
    return Color.GREEN

@traffic_light.on(Color.GREEN, TimerEvent)
def green_to_yellow(fsm, event) -> Color:
    print("🟢 → 🟡")
    return Color.YELLOW

@traffic_light.on(Color.YELLOW, TimerEvent)
def yellow_to_red(fsm, event) -> Color:
    print("🟡 → 🔴")
    return Color.RED

# Emergency overrides from any state
for color in Color:
    @traffic_light.on(color, EmergencyEvent)
    def emergency(fsm, event) -> Color:
        print("🚨 EMERGENCY → RED")
        return Color.RED
```

### Connection Manager with Retry Logic

```python
import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from pygenfsm import FSM

class ConnState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()

@dataclass
class ConnectEvent:
    host: str
    port: int

@dataclass
class ConnectionContext:
    retries: int = 0
    max_retries: int = 3
    last_error: str = ""

fsm = FSM[ConnState, ConnectEvent, ConnectionContext](
    state=ConnState.DISCONNECTED,
    context=ConnectionContext(),
)

@fsm.on(ConnState.DISCONNECTED, ConnectEvent)
async def start_connection(fsm, event: ConnectEvent) -> ConnState:
    print(f"🔌 Connecting to {event.host}:{event.port}")
    return ConnState.CONNECTING

@fsm.on(ConnState.CONNECTING, ConnectEvent)
async def attempt_connect(fsm, event: ConnectEvent) -> ConnState:
    try:
        # Simulate connection attempt
        await asyncio.sleep(1)
        if fsm.context.retries < 2:  # Simulate failures
            raise ConnectionError("Network timeout")
        
        print("✅ Connected!")
        fsm.context.retries = 0
        return ConnState.CONNECTED
        
    except ConnectionError as e:
        fsm.context.retries += 1
        fsm.context.last_error = str(e)
        
        if fsm.context.retries >= fsm.context.max_retries:
            print(f"❌ Max retries reached: {e}")
            return ConnState.ERROR
        
        print(f"🔄 Retry {fsm.context.retries}/{fsm.context.max_retries}")
        return ConnState.CONNECTING
```

## 🏗️ Advanced Patterns

### Late Context Injection with FSMBuilder

Perfect for dependency injection and testing:

```python
from pygenfsm import FSMBuilder

# Define builder without context
builder = FSMBuilder[State, Event, AppContext](
    initial_state=State.INIT
)

@builder.on(State.INIT, StartEvent)
async def initialize(fsm, event) -> State:
    # Access context that will be injected later
    await fsm.context.database.connect()
    return State.READY

# Later, when dependencies are ready...
database = Database(connection_string)
logger = Logger(level="INFO")

# Build FSM with context
fsm = builder.build(AppContext(
    database=database,
    logger=logger,
))
```

### Cloning for Testing Scenarios

Test different paths without affecting the original:

```python
# Create base FSM
original_fsm = FSM[State, Event, Context](
    state=State.INITIAL,
    context=Context(data=[]),
)

# Clone for testing
test_scenario_1 = original_fsm.clone()
test_scenario_2 = original_fsm.clone()

# Run different scenarios
await test_scenario_1.send(SuccessEvent())
await test_scenario_2.send(FailureEvent())

# Original remains unchanged
assert original_fsm.state == State.INITIAL
```

## 🔌 API Reference

### Core Classes

#### `FSM[S, E, C]`

The main FSM class with generic parameters:
- `S`: State enum type
- `E`: Event type (can be a Union)
- `C`: Context type

**Methods:**
- `on(state: S, event_type: type[E])`: Decorator to register handlers
- `async send(event: E) -> S`: Send event and transition state
- `send_sync(event: E) -> S`: Synchronous send (only for sync handlers)
- `clone() -> FSM[S, E, C]`: Create independent copy
- `replace_context(context: C) -> None`: Replace context

#### `FSMBuilder[S, E, C]`

Builder for late context injection:
- `on(state: S, event_type: type[E])`: Register handlers
- `build(context: C) -> FSM[S, E, C]`: Create FSM with context

### Best Practices

1. **Use sync handlers for:**
   - Simple state transitions
   - Pure computations
   - Context updates

2. **Use async handlers for:**
   - Network I/O
   - Database operations
   - File system access
   - Long computations

3. **Event Design:**
   - Make events immutable (use frozen dataclasses)
   - Include all necessary data in events
   - Use Union types for multiple events per state

4. **Context Design:**
   - Keep context focused and minimal
   - Use dataclasses for structure
   - Avoid circular references

## 🤝 Contributing

We love contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Setup development environment
git clone https://github.com/serialx/pygenfsm
cd pygenfsm
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run pyright .
```

## 📊 Comparison with transitions

### Feature Comparison

| Feature | pygenfsm | transitions |
|---------|----------|-------------|
| **Event Data** | ✅ First-class with dataclasses | ❌ Limited (callbacks, conditions) |
| **Async Support** | ✅ Native async/await | ❌ No built-in support |
| **Type Safety** | ✅ Full generics | ⚠️ Runtime checks only |
| **State Definition** | ✅ Enums (type-safe) | ⚠️ Strings/objects |
| **Handler Registration** | ✅ Decorators | ❌ Configuration dicts |
| **Context/Model** | ✅ Explicit, typed | ⚠️ Implicit on model |
| **Dependencies** | ✅ Zero | ❌ Multiple (six, etc.) |
| **Visualization** | ❌ Not built-in | ✅ GraphViz support |
| **Hierarchical States** | ❌ No | ✅ Yes (HSM) |
| **Parallel States** | ❌ No | ✅ Yes |
| **State History** | ❌ No | ✅ Yes |
| **Guards/Conditions** | ⚠️ In handler logic | ✅ Built-in |
| **Callbacks** | ⚠️ In handlers | ✅ before/after/prepare |
| **Size** | ~300 LOC | ~3000 LOC |

### When to Use Each

**Use pygenfsm when you need:**
- 🔒 Strong type safety with IDE support
- 🔄 Native async/await support
- 📦 Zero dependencies
- 🎯 Event-driven architecture with rich data
- 🚀 Modern Python patterns (3.11+)
- 🧪 Easy testing with full typing

**Use transitions when you need:**
- 📊 State diagram visualization
- 🎄 Hierarchical states (HSM)
- ⚡ Parallel state machines
- 📜 State history tracking
- 🔄 Complex transition guards/conditions
- 🏗️ Legacy Python support

## 🔗 Links

- **GitHub**: [github.com/serialx/pygenfsm](https://github.com/serialx/pygenfsm)
- **PyPI**: [pypi.org/project/pygenfsm](https://pypi.org/project/pygenfsm)
- **Documentation**: [Full API Docs](https://github.com/serialx/pygenfsm/wiki)
- **Issues**: [Report bugs or request features](https://github.com/serialx/pygenfsm/issues)

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ by developers who love clean state machines
</div>