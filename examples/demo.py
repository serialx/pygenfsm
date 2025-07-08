"""Demo script showing various FSM usage patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from pygenfsm import FSM


# Example 1: Traffic Light with timeout simulation
class TrafficState(Enum):
    RED = auto()
    YELLOW = auto()
    GREEN = auto()


class TrafficEvent(Enum):
    TIMER = auto()
    EMERGENCY = auto()


@dataclass
class TrafficData:
    cycles: int = 0
    emergency_mode: bool = False


# Type alias for cleaner code
TrafficFSM = FSM[TrafficState, TrafficEvent, TrafficData]

traffic_fsm = TrafficFSM(
    state=TrafficState.RED,
    data=TrafficData(),
)


@traffic_fsm.on(TrafficState.RED, TrafficEvent.TIMER)
def red_to_green(fsm: TrafficFSM, event: TrafficEvent) -> TrafficState:
    fsm.data.cycles += 1
    print("🔴 → 🟢 (RED to GREEN)")
    return TrafficState.GREEN


@traffic_fsm.on(TrafficState.GREEN, TrafficEvent.TIMER)
def green_to_yellow(fsm: TrafficFSM, event: TrafficEvent) -> TrafficState:
    print("🟢 → 🟡 (GREEN to YELLOW)")
    return TrafficState.YELLOW


@traffic_fsm.on(TrafficState.YELLOW, TrafficEvent.TIMER)
def yellow_to_red(fsm: TrafficFSM, event: TrafficEvent) -> TrafficState:
    print("🟡 → 🔴 (YELLOW to RED)")
    return TrafficState.RED


# Emergency handler for all states
for state in TrafficState:

    @traffic_fsm.on(state, TrafficEvent.EMERGENCY)
    def handle_emergency(fsm: TrafficFSM, event: TrafficEvent) -> TrafficState:
        fsm.data.emergency_mode = True
        print(f"⚠️  EMERGENCY from {fsm.state.name} → RED")
        return TrafficState.RED


# Example 2: Door Lock with access control
class DoorState(Enum):
    LOCKED = auto()
    UNLOCKED = auto()
    BLOCKED = auto()


class DoorEvent(Enum):
    UNLOCK = auto()
    LOCK = auto()
    BREACH_ATTEMPT = auto()
    RESET = auto()


@dataclass
class DoorData:
    failed_attempts: int = 0
    max_attempts: int = 3
    access_log: list[str] = field(default_factory=list)


# Type alias for cleaner code
DoorFSM = FSM[DoorState, DoorEvent, DoorData]

door_fsm = DoorFSM(
    state=DoorState.LOCKED,
    data=DoorData(),
)


@door_fsm.on(DoorState.LOCKED, DoorEvent.UNLOCK)
def unlock_door(fsm: DoorFSM, event: DoorEvent) -> DoorState:
    fsm.data.access_log.append("Door unlocked")
    fsm.data.failed_attempts = 0
    print("🔓 Door unlocked")
    return DoorState.UNLOCKED


@door_fsm.on(DoorState.UNLOCKED, DoorEvent.LOCK)
def lock_door(fsm: DoorFSM, event: DoorEvent) -> DoorState:
    fsm.data.access_log.append("Door locked")
    print("🔒 Door locked")
    return DoorState.LOCKED


@door_fsm.on(DoorState.LOCKED, DoorEvent.BREACH_ATTEMPT)
def handle_breach(fsm: DoorFSM, event: DoorEvent) -> DoorState:
    fsm.data.failed_attempts += 1
    fsm.data.access_log.append(f"Breach attempt #{fsm.data.failed_attempts}")

    if fsm.data.failed_attempts >= fsm.data.max_attempts:
        print(
            f"🚨 SECURITY ALERT: {fsm.data.failed_attempts} failed attempts - Door BLOCKED!"
        )
        return DoorState.BLOCKED
    else:
        print(f"⚠️  Failed attempt {fsm.data.failed_attempts}/{fsm.data.max_attempts}")
        return DoorState.LOCKED


@door_fsm.on(DoorState.BLOCKED, DoorEvent.RESET)
def reset_door(fsm: DoorFSM, event: DoorEvent) -> DoorState:
    fsm.data.failed_attempts = 0
    fsm.data.access_log.append("Security reset")
    print("🔄 Security reset - Door locked")
    return DoorState.LOCKED


if __name__ == "__main__":
    print("=== Traffic Light Demo ===")
    for _ in range(4):
        traffic_fsm.send(TrafficEvent.TIMER)

    print(f"\nTraffic light cycles: {traffic_fsm.data.cycles}")

    print("\n=== Emergency Test ===")
    traffic_fsm.send(TrafficEvent.EMERGENCY)

    print("\n\n=== Door Lock Demo ===")
    # Normal operation
    door_fsm.send(DoorEvent.UNLOCK)
    door_fsm.send(DoorEvent.LOCK)

    # Breach attempts
    print("\n=== Security Test ===")
    for _ in range(4):
        try:
            door_fsm.send(DoorEvent.BREACH_ATTEMPT)
        except RuntimeError as e:
            print(f"Error: {e}")

    # Reset after block
    door_fsm.send(DoorEvent.RESET)

    print("\n=== Access Log ===")
    for entry in door_fsm.data.access_log:
        print(f"  - {entry}")
