"""Tests for the FSM implementation."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

import pytest

from pygenfsm import FSM


class SimpleState(Enum):
    A = auto()
    B = auto()


@dataclass
class GoEvent:
    pass


@dataclass
class BackEvent:
    pass


SimpleEvent = Union[GoEvent, BackEvent]


@dataclass
class SimpleData:
    counter: int = 0


def test_basic_transition():
    """Test basic state transitions."""
    fsm = FSM[SimpleState, SimpleEvent, SimpleData](
        state=SimpleState.A,
        data=SimpleData(),
    )

    @fsm.on(SimpleState.A, GoEvent)
    def _a_to_b(  # pyright: ignore[reportUnusedFunction]
        fsm: FSM[SimpleState, SimpleEvent, SimpleData], event: GoEvent
    ) -> SimpleState:
        fsm.data.counter += 1
        return SimpleState.B

    @fsm.on(SimpleState.B, BackEvent)
    def _b_to_a(  # pyright: ignore[reportUnusedFunction]
        fsm: FSM[SimpleState, SimpleEvent, SimpleData], event: BackEvent
    ) -> SimpleState:
        fsm.data.counter += 1
        return SimpleState.A

    assert fsm.state == SimpleState.A
    assert fsm.data.counter == 0

    new_state = fsm.send(GoEvent())
    assert new_state == SimpleState.B
    assert fsm.state == SimpleState.B
    assert fsm.data.counter == 1

    new_state = fsm.send(BackEvent())
    assert new_state == SimpleState.A
    assert fsm.state == SimpleState.A
    expected_count = 2
    assert fsm.data.counter == expected_count


def test_missing_handler():
    """Test that missing handlers raise RuntimeError."""
    fsm = FSM[SimpleState, SimpleEvent, SimpleData](
        state=SimpleState.A,
        data=SimpleData(),
    )

    with pytest.raises(RuntimeError, match="No handler for"):
        fsm.send(GoEvent())
