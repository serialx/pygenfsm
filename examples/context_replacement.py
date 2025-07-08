"""Example: Demonstrating context replacement in FSM.

This example shows how to replace context in an existing FSM instance,
useful for scenarios like reconnecting with new connection objects.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum, auto

from pygenfsm import FSM


# States
class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTED = auto()


# Events
@dataclass
class ConnectEvent:
    pass


@dataclass
class DisconnectEvent:
    pass


@dataclass
class ReconnectEvent:
    """Reconnect with new connection object."""

    pass


# Context with connection object
@dataclass
class ConnectionContext:
    connection: Connection | None = None
    connection_count: int = 0


# Mock connection class
class Connection:
    def __init__(self, server: str):
        self.server = server
        self.id = id(self)  # Unique ID to track different instances

    def connect(self) -> None:
        print(f"🔌 Connected to {self.server} (connection id: {self.id})")

    def disconnect(self) -> None:
        print(f"👋 Disconnected from {self.server} (connection id: {self.id})")


# Type alias
ConnectionFSM = FSM[
    ConnectionState, ConnectEvent | DisconnectEvent | ReconnectEvent, ConnectionContext
]

# Create FSM with initial context
fsm = ConnectionFSM(
    state=ConnectionState.DISCONNECTED,
    context=ConnectionContext(),
)


# Handlers
@fsm.on(ConnectionState.DISCONNECTED, ConnectEvent)
def handle_connect(fsm: ConnectionFSM, event: ConnectEvent) -> ConnectionState:
    if fsm.context.connection is None:
        # Create new connection
        fsm.context.connection = Connection(f"server-{fsm.context.connection_count}")

    fsm.context.connection.connect()
    fsm.context.connection_count += 1
    return ConnectionState.CONNECTED


@fsm.on(ConnectionState.CONNECTED, DisconnectEvent)
def handle_disconnect(fsm: ConnectionFSM, event: DisconnectEvent) -> ConnectionState:
    if fsm.context.connection:
        fsm.context.connection.disconnect()
        fsm.context.connection = None
    return ConnectionState.DISCONNECTED


@fsm.on(ConnectionState.CONNECTED, ReconnectEvent)
def handle_reconnect(fsm: ConnectionFSM, event: ReconnectEvent) -> ConnectionState:
    print("\n🔄 Reconnecting with new connection object...")

    # Disconnect old connection
    if fsm.context.connection:
        fsm.context.connection.disconnect()

    # Create completely new context with new connection
    new_context = ConnectionContext(
        connection=Connection(f"new-server-{fsm.context.connection_count}"),
        connection_count=fsm.context.connection_count,
    )

    # Replace the entire context
    fsm.replace_context(new_context)

    # Connect with new connection
    if fsm.context.connection:
        fsm.context.connection.connect()
    fsm.context.connection_count += 1

    return ConnectionState.CONNECTED


# Demo usage
async def main():
    print("=== Context Replacement Demo ===\n")

    # Initial connection
    print("1. Initial connection:")
    await fsm.send(ConnectEvent())
    print(f"   State: {fsm.state.name}")
    print(f"   Connection count: {fsm.context.connection_count}\n")

    # Reconnect with new connection object
    print("2. Reconnecting (replaces context):")
    await fsm.send(ReconnectEvent())
    print(f"   State: {fsm.state.name}")
    print(f"   Connection count: {fsm.context.connection_count}\n")

    # Another reconnect
    print("3. Another reconnect:")
    await fsm.send(ReconnectEvent())
    print(f"   State: {fsm.state.name}")
    print(f"   Connection count: {fsm.context.connection_count}\n")

    # Normal disconnect
    print("4. Normal disconnect:")
    await fsm.send(DisconnectEvent())
    print(f"   State: {fsm.state.name}")


if __name__ == "__main__":
    asyncio.run(main())
