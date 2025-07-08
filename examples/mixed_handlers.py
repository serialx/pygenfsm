"""Example: FSM with both sync and async handlers."""

import asyncio
from dataclasses import dataclass
from enum import Enum, auto

from pygenfsm import FSM


class ProcessState(Enum):
    IDLE = auto()
    LOADING = auto()
    PROCESSING = auto()
    DONE = auto()


@dataclass
class StartEvent:
    filename: str


@dataclass
class DataLoadedEvent:
    size: int


@dataclass
class ProcessCompleteEvent:
    result: str


@dataclass
class ResetEvent:
    pass


# Union type for events
ProcessEvent = StartEvent | DataLoadedEvent | ProcessCompleteEvent | ResetEvent


@dataclass
class ProcessContext:
    filename: str = ""
    data_size: int = 0
    result: str = ""


# Type alias
ProcessFSM = FSM[ProcessState, ProcessEvent, ProcessContext]

# Create FSM
fsm = ProcessFSM(
    state=ProcessState.IDLE,
    context=ProcessContext(),
)


# Sync handler - for simple state transitions
@fsm.on(ProcessState.IDLE, StartEvent)
def start_loading(fsm: ProcessFSM, event: StartEvent) -> ProcessState:
    """Simple sync handler for starting the process."""
    fsm.context.filename = event.filename
    print(f"Starting to load: {event.filename}")
    return ProcessState.LOADING


# Async handler - for I/O operations
@fsm.on(ProcessState.LOADING, DataLoadedEvent)
async def data_loaded(fsm: ProcessFSM, event: DataLoadedEvent) -> ProcessState:
    """Async handler simulating data loading."""
    fsm.context.data_size = event.size
    print(f"Loading {event.size} bytes...")

    # Simulate async I/O operation
    await asyncio.sleep(0.1)

    print("Data loaded, starting processing")
    return ProcessState.PROCESSING


# Async handler - for CPU-intensive operations
@fsm.on(ProcessState.PROCESSING, ProcessCompleteEvent)
async def process_complete(
    fsm: ProcessFSM, event: ProcessCompleteEvent
) -> ProcessState:
    """Async handler for processing completion."""
    fsm.context.result = event.result

    # Simulate async processing
    await asyncio.sleep(0.05)

    print(f"Processing complete: {event.result}")
    return ProcessState.DONE


# Sync handler - for simple reset
@fsm.on(ProcessState.DONE, ResetEvent)
def reset(fsm: ProcessFSM, event: ResetEvent) -> ProcessState:
    """Simple sync handler for reset."""
    # Clear context
    fsm.context.filename = ""
    fsm.context.data_size = 0
    fsm.context.result = ""
    print("System reset")
    return ProcessState.IDLE


async def main():
    """Demonstrate mixed sync/async handlers."""
    print("=== FSM with Mixed Sync/Async Handlers ===\n")

    # Start with sync handler
    await fsm.send(StartEvent(filename="data.csv"))

    # Continue with async handler
    await fsm.send(DataLoadedEvent(size=1024))

    # Another async handler
    await fsm.send(ProcessCompleteEvent(result="Success: 42 records processed"))

    # End with sync handler
    await fsm.send(ResetEvent())

    print(f"\nFinal state: {fsm.state}")
    print("\nThis example shows that:")
    print("- Simple state transitions can use sync handlers")
    print("- I/O or CPU-intensive operations can use async handlers")
    print("- Both work seamlessly with await fsm.send()")


if __name__ == "__main__":
    asyncio.run(main())
