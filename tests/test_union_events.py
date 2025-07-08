"""Tests for FSM with union event types."""

from dataclasses import dataclass
from enum import Enum, auto

import pytest

from pygenfsm import FSM


class DoorState(Enum):
    LOCKED = auto()
    UNLOCKED = auto()


@dataclass
class UnlockEvent:
    code: str


@dataclass
class LockEvent:
    auto_lock: bool = False


@dataclass
class ForceOpenEvent:
    admin_override: bool


# Union type for events
DoorEvent = UnlockEvent | LockEvent | ForceOpenEvent


@dataclass
class DoorContext:
    unlock_attempts: int = 0
    last_code: str = ""


@pytest.mark.asyncio
async def test_union_event_types():
    """Test that FSM works correctly with union event types."""
    # Create FSM with union event type
    fsm = FSM[DoorState, DoorEvent, DoorContext](
        state=DoorState.LOCKED,
        context=DoorContext(),
    )

    # Register handlers for specific event types
    @fsm.on(DoorState.LOCKED, UnlockEvent)
    async def _unlock(  # pyright: ignore[reportUnusedFunction]
        fsm: FSM[DoorState, DoorEvent, DoorContext], event: UnlockEvent
    ) -> DoorState:
        fsm.context.unlock_attempts += 1
        fsm.context.last_code = event.code
        return DoorState.UNLOCKED

    @fsm.on(DoorState.UNLOCKED, LockEvent)
    async def _lock(  # pyright: ignore[reportUnusedFunction]
        fsm: FSM[DoorState, DoorEvent, DoorContext], event: LockEvent
    ) -> DoorState:
        return DoorState.LOCKED

    @fsm.on(DoorState.LOCKED, ForceOpenEvent)
    async def _force_open(  # pyright: ignore[reportUnusedFunction]
        fsm: FSM[DoorState, DoorEvent, DoorContext], event: ForceOpenEvent
    ) -> DoorState:
        if event.admin_override:
            return DoorState.UNLOCKED
        return DoorState.LOCKED

    # Test unlock
    assert fsm.state == DoorState.LOCKED
    await fsm.send(UnlockEvent(code="1234"))
    assert fsm.state == DoorState.UNLOCKED
    assert fsm.context.unlock_attempts == 1
    assert fsm.context.last_code == "1234"

    # Test lock
    await fsm.send(LockEvent(auto_lock=True))
    assert fsm.state == DoorState.LOCKED

    # Test force open without override
    await fsm.send(ForceOpenEvent(admin_override=False))
    assert fsm.state == DoorState.LOCKED

    # Test force open with override
    await fsm.send(ForceOpenEvent(admin_override=True))
    assert fsm.state == DoorState.UNLOCKED


@pytest.mark.asyncio
async def test_missing_handler_with_union():
    """Test that missing handlers raise appropriate errors with union types."""
    fsm = FSM[DoorState, DoorEvent, DoorContext](
        state=DoorState.LOCKED,
        context=DoorContext(),
    )

    # No handler registered for UnlockEvent
    with pytest.raises(RuntimeError, match="No handler for.*UnlockEvent"):
        await fsm.send(UnlockEvent(code="test"))
