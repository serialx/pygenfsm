"""Example: Demonstrating context injection after FSM creation.

This example shows how to use FSMBuilder to define FSM behavior
before context is available, then create instances when dependencies
(like database connections) become available.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from pygenfsm import FSM, FSMBuilder


# States
class ServiceState(Enum):
    UNINITIALIZED = auto()
    READY = auto()
    PROCESSING = auto()
    ERROR = auto()


# Events
@dataclass
class InitializeEvent:
    """Initialize the service with injected dependencies."""

    pass


@dataclass
class ProcessRequestEvent:
    """Process a request using the injected services."""

    request_id: str
    data: dict[str, Any]


@dataclass
class CompleteEvent:
    """Processing completed successfully."""

    result: Any


@dataclass
class ErrorEvent:
    """An error occurred."""

    error: str


# Union type for events
ServiceEvent = InitializeEvent | ProcessRequestEvent | CompleteEvent | ErrorEvent


# Context with external dependencies
@dataclass
class ServiceContext:
    """Context containing external service dependencies."""

    db_connection: DatabaseConnection
    cache: CacheService
    logger: Logger
    request_count: int = 0
    last_error: str | None = None


# Mock service classes
class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected = False

    def connect(self) -> None:
        self.connected = True
        print(f"📊 Connected to database: {self.connection_string}")

    def query(self, request_id: str) -> dict[str, Any]:
        return {"id": request_id, "status": "found", "data": "sample data"}


class CacheService:
    def __init__(self, host: str):
        self.host = host
        self.cache: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value
        print(f"💾 Cached: {key}")


class Logger:
    def __init__(self, name: str):
        self.name = name

    def info(self, message: str) -> None:
        print(f"ℹ️  [{self.name}] {message}")

    def error(self, message: str) -> None:
        print(f"❌ [{self.name}] {message}")


# Create FSM builder
builder = FSMBuilder[ServiceState, ServiceEvent, ServiceContext](
    initial_state=ServiceState.UNINITIALIZED
)


# Handlers
# Type alias for cleaner code
ServiceFSM = FSM[ServiceState, ServiceEvent, ServiceContext]


@builder.on(ServiceState.UNINITIALIZED, InitializeEvent)
def initialize(fsm: ServiceFSM, event: InitializeEvent) -> ServiceState:
    fsm.context.db_connection.connect()
    fsm.context.logger.info("Service initialized successfully")
    return ServiceState.READY


@builder.on(ServiceState.READY, ProcessRequestEvent)
def process_request(fsm: ServiceFSM, event: ProcessRequestEvent) -> ServiceState:
    fsm.context.logger.info(f"Processing request {event.request_id}")
    fsm.context.request_count += 1

    # Check cache first
    cached = fsm.context.cache.get(event.request_id)
    if cached:
        print(f"✅ Found in cache: {event.request_id}")
        return ServiceState.PROCESSING

    # Query database
    result = fsm.context.db_connection.query(event.request_id)
    fsm.context.cache.set(event.request_id, result)

    return ServiceState.PROCESSING


@builder.on(ServiceState.PROCESSING, CompleteEvent)
def complete_processing(fsm: ServiceFSM, event: CompleteEvent) -> ServiceState:
    fsm.context.logger.info(
        f"Processing completed. Total requests: {fsm.context.request_count}"
    )
    return ServiceState.READY


@builder.on(ServiceState.ERROR, InitializeEvent)
def reinitialize(fsm: ServiceFSM, event: InitializeEvent) -> ServiceState:
    print("🔄 Attempting to reinitialize from error state...")
    return initialize(fsm, event)


# Demo usage
if __name__ == "__main__":
    print("=== Context Injection Demo ===\n")

    # First, demonstrate that we can't build without context
    print("1. FSM builder is ready, but no instances yet\n")

    # Create dependencies (simulating late initialization)
    print("2. Creating external dependencies...")
    db = DatabaseConnection("postgresql://localhost/myapp")
    cache = CacheService("redis://localhost:6379")
    logger = Logger("ServiceFSM")

    # Create context and build FSM
    print("\n3. Building FSM with context...")
    context = ServiceContext(
        db_connection=db,
        cache=cache,
        logger=logger,
    )
    service_fsm = builder.build(context)
    print("   ✅ FSM instance created with context\n")

    # Initialize
    print("4. Initializing service:")
    service_fsm.send(InitializeEvent())
    print(f"   State: {service_fsm.state.name}\n")

    # Process some requests
    print("5. Processing requests:")
    service_fsm.send(
        ProcessRequestEvent(request_id="req_001", data={"action": "fetch"})
    )
    service_fsm.send(CompleteEvent(result={"status": "success"}))

    service_fsm.send(
        ProcessRequestEvent(request_id="req_002", data={"action": "update"})
    )
    service_fsm.send(CompleteEvent(result={"status": "success"}))

    # Try cached request
    service_fsm.send(
        ProcessRequestEvent(request_id="req_001", data={"action": "fetch"})
    )
    service_fsm.send(CompleteEvent(result={"status": "success"}))

    print(f"\nFinal state: {service_fsm.state.name}")
    print(f"Total requests processed: {service_fsm.context.request_count}")

    # Demonstrate creating another instance with different context
    print("\n6. Creating another FSM instance with different context:")
    db2 = DatabaseConnection("postgresql://localhost/myapp2")
    cache2 = CacheService("redis://localhost:6380")
    logger2 = Logger("ServiceFSM2")

    context2 = ServiceContext(
        db_connection=db2,
        cache=cache2,
        logger=logger2,
    )
    service_fsm2 = builder.build(context2)
    service_fsm2.send(InitializeEvent())
    print("   ✅ Second instance created and initialized")
    print("   Both instances share behavior but have separate state/context")
