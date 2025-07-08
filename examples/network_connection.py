"""Example: Network connection manager with complex event types carrying data."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Union

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
    retry_after: Optional[float] = None


@dataclass
class DataReceivedEvent:
    """Data received from server."""

    data: bytes
    timestamp: float


class DisconnectEvent:
    """Request to disconnect."""

    pass


class RetryEvent:
    """Retry connection attempt."""

    pass


# Union type for all events (use Union for Python 3.8 compatibility)
ConnectionEvent = Union[
    ConnectEvent,
    ConnectionEstablishedEvent,
    ConnectionErrorEvent,
    DataReceivedEvent,
    DisconnectEvent,
    RetryEvent,
]


# Connection data
@dataclass
class ConnectionData:
    current_host: Optional[str] = None
    current_port: Optional[int] = None
    session_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    bytes_received: int = 0


# Type alias
ConnectionFSM = FSM[ConnectionState, ConnectionEvent, ConnectionData]

# Create FSM
connection = ConnectionFSM(
    state=ConnectionState.DISCONNECTED,
    data=ConnectionData(),
)


# Handler for DISCONNECTED state
@connection.on(ConnectionState.DISCONNECTED, ConnectEvent)
def start_connection(fsm: ConnectionFSM, event: ConnectEvent) -> ConnectionState:
    print(f"🔌 Connecting to {event.host}:{event.port} (timeout: {event.timeout}s)")
    fsm.data.current_host = event.host
    fsm.data.current_port = event.port
    fsm.data.retry_count = 0
    return ConnectionState.CONNECTING


# Handler for CONNECTING state - success
@connection.on(ConnectionState.CONNECTING, ConnectionEstablishedEvent)
def connection_established(
    fsm: ConnectionFSM, event: ConnectionEstablishedEvent
) -> ConnectionState:
    print(f"✅ Connected! Session: {event.session_id}, Latency: {event.latency_ms}ms")
    fsm.data.session_id = event.session_id
    fsm.data.last_error = None
    return ConnectionState.CONNECTED


# Handler for CONNECTING state - error
@connection.on(ConnectionState.CONNECTING, ConnectionErrorEvent)
def connection_failed(
    fsm: ConnectionFSM, event: ConnectionErrorEvent
) -> ConnectionState:
    print(f"❌ Connection failed: [{event.error_code}] {event.message}")
    fsm.data.last_error = event.message

    if fsm.data.retry_count < fsm.data.max_retries:
        fsm.data.retry_count += 1
        print(f"🔄 Will retry ({fsm.data.retry_count}/{fsm.data.max_retries})")
        if event.retry_after:
            print(f"   Waiting {event.retry_after}s before retry...")
        return ConnectionState.RECONNECTING
    else:
        print("❌ Max retries exceeded. Going to ERROR state.")
        return ConnectionState.ERROR


# Handler for CONNECTED state - receive data
@connection.on(ConnectionState.CONNECTED, DataReceivedEvent)
def handle_data(fsm: ConnectionFSM, event: DataReceivedEvent) -> ConnectionState:
    fsm.data.bytes_received += len(event.data)
    print(f"📦 Received {len(event.data)} bytes (total: {fsm.data.bytes_received})")
    return ConnectionState.CONNECTED


# Handler for CONNECTED state - disconnect
@connection.on(ConnectionState.CONNECTED, DisconnectEvent)
def disconnect(fsm: ConnectionFSM, event: DisconnectEvent) -> ConnectionState:
    print(f"👋 Disconnecting from {fsm.data.current_host}:{fsm.data.current_port}")
    print(f"   Session {fsm.data.session_id} ended")
    print(f"   Total bytes received: {fsm.data.bytes_received}")

    # Clear connection data
    fsm.data.current_host = None
    fsm.data.current_port = None
    fsm.data.session_id = None
    fsm.data.bytes_received = 0

    return ConnectionState.DISCONNECTED


# Handler for CONNECTED state - error
@connection.on(ConnectionState.CONNECTED, ConnectionErrorEvent)
def connection_lost(fsm: ConnectionFSM, event: ConnectionErrorEvent) -> ConnectionState:
    print(f"⚠️  Connection lost: [{event.error_code}] {event.message}")
    fsm.data.last_error = event.message
    fsm.data.retry_count = 0
    return ConnectionState.RECONNECTING


# Handler for RECONNECTING state
@connection.on(ConnectionState.RECONNECTING, RetryEvent)
def retry_connection(fsm: ConnectionFSM, event: RetryEvent) -> ConnectionState:
    print(f"🔄 Retrying connection to {fsm.data.current_host}:{fsm.data.current_port}")
    return ConnectionState.CONNECTING


# Handler for ERROR state - can only disconnect
@connection.on(ConnectionState.ERROR, DisconnectEvent)
def error_disconnect(fsm: ConnectionFSM, event: DisconnectEvent) -> ConnectionState:
    print("🔴 Clearing error state and disconnecting")
    fsm.data.last_error = None
    fsm.data.retry_count = 0
    return ConnectionState.DISCONNECTED


# Demo usage
if __name__ == "__main__":
    print("=== Network Connection FSM Demo ===\n")

    # Initial connection attempt
    connection.send(ConnectEvent(host="api.example.com", port=443, timeout=10.0))

    # Simulate connection error with retry
    connection.send(
        ConnectionErrorEvent(
            error_code=503, message="Service temporarily unavailable", retry_after=2.0
        )
    )

    # Retry
    connection.send(RetryEvent())

    # Successful connection
    connection.send(
        ConnectionEstablishedEvent(session_id="sess_123abc", latency_ms=45.3)
    )

    # Receive some data
    import time

    for i in range(3):
        connection.send(
            DataReceivedEvent(data=f"Packet {i}".encode(), timestamp=time.time())
        )

    # Connection error while connected
    connection.send(ConnectionErrorEvent(error_code=1001, message="Connection timeout"))

    # Retry and succeed
    connection.send(RetryEvent())
    connection.send(
        ConnectionEstablishedEvent(session_id="sess_456def", latency_ms=52.1)
    )

    # Clean disconnect
    connection.send(DisconnectEvent())

    print(f"\nFinal state: {connection.state.name}")
    print(f"Last error: {connection.data.last_error}")
