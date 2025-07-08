"""Example: Network connection manager with complex event types carrying data."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum, auto

from pygenfsm import FSM


# States
class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    RECONNECTING = auto()
    ERROR = auto()


# Complex events with data
@dataclass
class ConnectEvent:
    """Request to connect to a server."""

    host: str
    port: int
    timeout: float = 30.0


@dataclass
class ConnectionEstablishedEvent:
    """Connection successfully established."""

    session_id: str
    latency_ms: float


@dataclass
class ConnectionErrorEvent:
    """Connection error occurred."""

    error_code: int
    message: str
    retry_after: float | None = None


@dataclass
class ContextReceivedEvent:
    """Context received from server."""

    data: bytes
    timestamp: float


@dataclass
class DisconnectEvent:
    """Request to disconnect."""

    pass


@dataclass
class RetryEvent:
    """Retry connection attempt."""

    pass


# Union type for all events
ConnectionEvent = (
    ConnectEvent
    | ConnectionEstablishedEvent
    | ConnectionErrorEvent
    | ContextReceivedEvent
    | DisconnectEvent
    | RetryEvent
)


# Connection data
@dataclass
class ConnectionContext:
    current_host: str | None = None
    current_port: int | None = None
    session_id: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    last_error: str | None = None
    bytes_received: int = 0


# Type alias
ConnectionFSM = FSM[ConnectionState, ConnectionEvent, ConnectionContext]

# Create FSM
connection = ConnectionFSM(
    state=ConnectionState.DISCONNECTED,
    context=ConnectionContext(),
)


# Handler for DISCONNECTED state
@connection.on(ConnectionState.DISCONNECTED, ConnectEvent)
def start_connection(fsm: ConnectionFSM, event: ConnectEvent) -> ConnectionState:
    print(f"🔌 Connecting to {event.host}:{event.port} (timeout: {event.timeout}s)")
    fsm.context.current_host = event.host
    fsm.context.current_port = event.port
    fsm.context.retry_count = 0
    return ConnectionState.CONNECTING


# Handler for CONNECTING state - success
@connection.on(ConnectionState.CONNECTING, ConnectionEstablishedEvent)
def connection_established(
    fsm: ConnectionFSM, event: ConnectionEstablishedEvent
) -> ConnectionState:
    print(f"✅ Connected! Session: {event.session_id}, Latency: {event.latency_ms}ms")
    fsm.context.session_id = event.session_id
    fsm.context.last_error = None
    return ConnectionState.CONNECTED


# Handler for CONNECTING state - error
@connection.on(ConnectionState.CONNECTING, ConnectionErrorEvent)
def connection_failed(
    fsm: ConnectionFSM, event: ConnectionErrorEvent
) -> ConnectionState:
    print(f"❌ Connection failed: [{event.error_code}] {event.message}")
    fsm.context.last_error = event.message

    if fsm.context.retry_count < fsm.context.max_retries:
        fsm.context.retry_count += 1
        print(f"🔄 Will retry ({fsm.context.retry_count}/{fsm.context.max_retries})")
        if event.retry_after:
            print(f"   Waiting {event.retry_after}s before retry...")
        return ConnectionState.RECONNECTING
    else:
        print("❌ Max retries exceeded. Going to ERROR state.")
        return ConnectionState.ERROR


# Handler for CONNECTED state - receive data
@connection.on(ConnectionState.CONNECTED, ContextReceivedEvent)
def handle_data(fsm: ConnectionFSM, event: ContextReceivedEvent) -> ConnectionState:
    fsm.context.bytes_received += len(event.data)
    print(f"📦 Received {len(event.data)} bytes (total: {fsm.context.bytes_received})")
    return ConnectionState.CONNECTED


# Handler for CONNECTED state - disconnect
@connection.on(ConnectionState.CONNECTED, DisconnectEvent)
def disconnect(fsm: ConnectionFSM, event: DisconnectEvent) -> ConnectionState:
    print(
        f"👋 Disconnecting from {fsm.context.current_host}:{fsm.context.current_port}"
    )
    print(f"   Session {fsm.context.session_id} ended")
    print(f"   Total bytes received: {fsm.context.bytes_received}")

    # Clear connection data
    fsm.context.current_host = None
    fsm.context.current_port = None
    fsm.context.session_id = None
    fsm.context.bytes_received = 0

    return ConnectionState.DISCONNECTED


# Handler for CONNECTED state - error
@connection.on(ConnectionState.CONNECTED, ConnectionErrorEvent)
def connection_lost(fsm: ConnectionFSM, event: ConnectionErrorEvent) -> ConnectionState:
    print(f"⚠️  Connection lost: [{event.error_code}] {event.message}")
    fsm.context.last_error = event.message
    fsm.context.retry_count = 0
    return ConnectionState.RECONNECTING


# Handler for RECONNECTING state
@connection.on(ConnectionState.RECONNECTING, RetryEvent)
def retry_connection(fsm: ConnectionFSM, event: RetryEvent) -> ConnectionState:
    print(
        f"🔄 Retrying connection to {fsm.context.current_host}:{fsm.context.current_port}"
    )
    return ConnectionState.CONNECTING


# Handler for ERROR state - can only disconnect
@connection.on(ConnectionState.ERROR, DisconnectEvent)
def error_disconnect(fsm: ConnectionFSM, event: DisconnectEvent) -> ConnectionState:
    print("🔴 Clearing error state and disconnecting")
    fsm.context.last_error = None
    fsm.context.retry_count = 0
    return ConnectionState.DISCONNECTED


# Demo usage
async def main():
    print("=== Network Connection FSM Demo ===\n")

    # Initial connection attempt
    await connection.send(ConnectEvent(host="api.example.com", port=443, timeout=10.0))

    # Simulate connection error with retry
    await connection.send(
        ConnectionErrorEvent(
            error_code=503, message="Service temporarily unavailable", retry_after=2.0
        )
    )

    # Retry
    await connection.send(RetryEvent())

    # Successful connection
    await connection.send(
        ConnectionEstablishedEvent(session_id="sess_123abc", latency_ms=45.3)
    )

    # Receive some data
    import time

    for i in range(3):
        await connection.send(
            ContextReceivedEvent(data=f"Packet {i}".encode(), timestamp=time.time())
        )

    # Connection error while connected
    await connection.send(
        ConnectionErrorEvent(error_code=1001, message="Connection timeout")
    )

    # Retry and succeed
    await connection.send(RetryEvent())
    await connection.send(
        ConnectionEstablishedEvent(session_id="sess_456def", latency_ms=52.1)
    )

    # Clean disconnect
    await connection.send(DisconnectEvent())

    print(f"\nFinal state: {connection.state.name}")
    print(f"Last error: {connection.context.last_error}")


if __name__ == "__main__":
    asyncio.run(main())
