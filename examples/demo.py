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


@dataclass
class TimerEvent:
    pass


@dataclass
class EmergencyEvent:
    pass


@dataclass
class TrafficData:
    cycles: int = 0
    emergency_mode: bool = False


# Union type for traffic events
TrafficEvent = TimerEvent | EmergencyEvent

# Type alias for cleaner code
TrafficFSM = FSM[TrafficState, TrafficEvent, TrafficData]

traffic_fsm = TrafficFSM(
    state=TrafficState.RED,
    data=TrafficData(),
)


@traffic_fsm.on(TrafficState.RED, TimerEvent)
def red_to_green(fsm: TrafficFSM, event: TimerEvent) -> TrafficState:
    fsm.data.cycles += 1
    print("🔴 → 🟢 (RED to GREEN)")
    return TrafficState.GREEN


@traffic_fsm.on(TrafficState.GREEN, TimerEvent)
def green_to_yellow(fsm: TrafficFSM, event: TimerEvent) -> TrafficState:
    print("🟢 → 🟡 (GREEN to YELLOW)")
    return TrafficState.YELLOW


@traffic_fsm.on(TrafficState.YELLOW, TimerEvent)
def yellow_to_red(fsm: TrafficFSM, event: TimerEvent) -> TrafficState:
    print("🟡 → 🔴 (YELLOW to RED)")
    return TrafficState.RED


# Emergency handler for all states
for state in TrafficState:

    @traffic_fsm.on(state, EmergencyEvent)
    def handle_emergency(fsm: TrafficFSM, event: EmergencyEvent) -> TrafficState:
        fsm.data.emergency_mode = True
        print(f"⚠️  EMERGENCY from {fsm.state.name} → RED")
        return TrafficState.RED


# Example 2: Door Lock with access control
class DoorState(Enum):
    LOCKED = auto()
    UNLOCKED = auto()
    BLOCKED = auto()


@dataclass
class UnlockEvent:
    pass


@dataclass
class LockEvent:
    pass


@dataclass
class BreachAttemptEvent:
    pass


@dataclass
class ResetEvent:
    pass


@dataclass
class DoorData:
    failed_attempts: int = 0
    max_attempts: int = 3
    access_log: list[str] = field(default_factory=lambda: [])


# Union type for door events
DoorEvent = UnlockEvent | LockEvent | BreachAttemptEvent | ResetEvent

# Type alias for cleaner code
DoorFSM = FSM[DoorState, DoorEvent, DoorData]

door_fsm = DoorFSM(
    state=DoorState.LOCKED,
    data=DoorData(),
)


@door_fsm.on(DoorState.LOCKED, UnlockEvent)
def unlock_door(fsm: DoorFSM, event: UnlockEvent) -> DoorState:
    fsm.data.access_log.append("Door unlocked")
    fsm.data.failed_attempts = 0
    print("🔓 Door unlocked")
    return DoorState.UNLOCKED


@door_fsm.on(DoorState.UNLOCKED, LockEvent)
def lock_door(fsm: DoorFSM, event: LockEvent) -> DoorState:
    fsm.data.access_log.append("Door locked")
    print("🔒 Door locked")
    return DoorState.LOCKED


@door_fsm.on(DoorState.LOCKED, BreachAttemptEvent)
def handle_breach(fsm: DoorFSM, event: BreachAttemptEvent) -> DoorState:
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


@door_fsm.on(DoorState.BLOCKED, ResetEvent)
def reset_door(fsm: DoorFSM, event: ResetEvent) -> DoorState:
    fsm.data.failed_attempts = 0
    fsm.data.access_log.append("Security reset")
    print("🔄 Security reset - Door locked")
    return DoorState.LOCKED


if __name__ == "__main__":
    print("=== Traffic Light Demo ===")
    for _ in range(4):
        traffic_fsm.send(TimerEvent())

    print(f"\nTraffic light cycles: {traffic_fsm.data.cycles}")

    print("\n=== Emergency Test ===")
    traffic_fsm.send(EmergencyEvent())

    print("\n\n=== Door Lock Demo ===")
    # Normal operation
    door_fsm.send(UnlockEvent())
    door_fsm.send(LockEvent())

    # Breach attempts
    print("\n=== Security Test ===")
    for _ in range(4):
        try:
            door_fsm.send(BreachAttemptEvent())
        except RuntimeError as e:
            print(f"Error: {e}")

    # Reset after block
    door_fsm.send(ResetEvent())

    print("\n=== Access Log ===")
    for entry in door_fsm.data.access_log:
        print(f"  - {entry}")
