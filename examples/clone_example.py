"""Example demonstrating FSM cloning functionality."""

from dataclasses import dataclass, field
from enum import Enum, auto

from pygenfsm import FSM


# States
class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


# Events
@dataclass
class StartEvent:
    """Start the task."""

    worker_id: int


@dataclass
class CompleteEvent:
    """Complete the task successfully."""

    result: str


@dataclass
class FailEvent:
    """Task failed."""

    error: str


# Union of all events
TaskEvent = StartEvent | CompleteEvent | FailEvent


# Context
@dataclass
class TaskContext:
    attempts: int = 0
    worker_ids: list[int] = field(default_factory=lambda: [])
    results: list[str] = field(default_factory=lambda: [])
    errors: list[str] = field(default_factory=lambda: [])


# Type alias
TaskFSM = FSM[TaskState, TaskEvent, TaskContext]


"""Create and configure a task FSM."""
fsm = TaskFSM(
    state=TaskState.PENDING,
    context=TaskContext(),
)


@fsm.on(TaskState.PENDING, StartEvent)
def start_task(fsm: TaskFSM, event: StartEvent) -> TaskState:
    fsm.context.attempts += 1
    fsm.context.worker_ids.append(event.worker_id)
    print(
        f"🚀 Task started by worker {event.worker_id} (attempt #{fsm.context.attempts})"
    )
    return TaskState.RUNNING


@fsm.on(TaskState.RUNNING, CompleteEvent)
def complete_task(fsm: TaskFSM, event: CompleteEvent) -> TaskState:
    fsm.context.results.append(event.result)
    print(f"✅ Task completed: {event.result}")
    return TaskState.COMPLETED


@fsm.on(TaskState.RUNNING, FailEvent)
def fail_task(fsm: TaskFSM, event: FailEvent) -> TaskState:
    fsm.context.errors.append(event.error)
    print(f"❌ Task failed: {event.error}")
    return TaskState.FAILED


@fsm.on(TaskState.FAILED, StartEvent)
def retry_task(fsm: TaskFSM, event: StartEvent) -> TaskState:
    fsm.context.attempts += 1
    fsm.context.worker_ids.append(event.worker_id)
    print(
        f"🔄 Retrying task with worker {event.worker_id} (attempt #{fsm.context.attempts})"
    )
    return TaskState.RUNNING


def create_task_fsm() -> TaskFSM:
    """Create and return a new task FSM instance."""
    return fsm.clone()  # Clone the original FSM to create a new instance


if __name__ == "__main__":
    print("=== FSM Cloning Example ===\n")

    # Create original task FSM
    original_task = create_task_fsm()

    # Start and fail the original task
    original_task.send(StartEvent(worker_id=1))
    original_task.send(FailEvent(error="Network timeout"))

    # Clone the FSM to try different scenarios
    print("\n--- Cloning FSM for scenario testing ---\n")

    # Scenario 1: Retry with same worker
    scenario1 = original_task.clone()
    print("Scenario 1: Retry with same worker")
    scenario1.send(StartEvent(worker_id=1))
    scenario1.send(CompleteEvent(result="Success with retry"))

    # Scenario 2: Retry with different worker
    scenario2 = original_task.clone()
    print("\nScenario 2: Retry with different worker")
    scenario2.send(StartEvent(worker_id=2))
    scenario2.send(CompleteEvent(result="Success with different worker"))

    # Scenario 3: Multiple failures
    scenario3 = original_task.clone()
    print("\nScenario 3: Multiple failures")
    scenario3.send(StartEvent(worker_id=3))
    scenario3.send(FailEvent(error="Disk full"))
    scenario3.send(StartEvent(worker_id=4))
    scenario3.send(FailEvent(error="Out of memory"))

    # Show that original is unaffected
    print("\n--- Original FSM State ---")
    print(f"State: {original_task.state.name}")
    print(f"Attempts: {original_task.context.attempts}")
    print(f"Worker IDs: {original_task.context.worker_ids}")
    print(f"Errors: {original_task.context.errors}")

    print("\n--- Scenario Results ---")
    print(
        f"Scenario 1 - State: {scenario1.state.name}, Results: {scenario1.context.results}"
    )
    print(
        f"Scenario 2 - State: {scenario2.state.name}, Results: {scenario2.context.results}"
    )
    print(
        f"Scenario 3 - State: {scenario3.state.name}, Attempts: {scenario3.context.attempts}, Errors: {scenario3.context.errors}"
    )

    # Example: Creating a pool of identical FSMs
    print("\n--- FSM Pool Example ---")
    fsm_pool = [create_task_fsm() for _ in range(3)]

    # Process tasks in parallel (conceptually)
    for i, fsm in enumerate(fsm_pool):
        fsm.send(StartEvent(worker_id=i + 10))
        if i == 1:
            fsm.send(FailEvent(error="Random failure"))
        else:
            fsm.send(CompleteEvent(result=f"Task {i} completed"))

    print("\nPool results:")
    for i, fsm in enumerate(fsm_pool):
        print(f"  FSM {i}: {fsm.state.name}")
