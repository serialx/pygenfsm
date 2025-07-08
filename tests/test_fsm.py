"""Tests for the FSM implementation."""

from dataclasses import dataclass
from enum import Enum, auto

import pytest

from pygenfsm import FSM


class TestState(Enum):
    A = auto()
    B = auto()


class TestEvent(Enum):
    GO = auto()
    BACK = auto()


@dataclass
class TestData:
    counter: int = 0


def test_basic_transition():
    """Test basic state transitions."""
    fsm = FSM[TestState, TestEvent, TestData](
        state=TestState.A,
        data=TestData(),
    )

    @fsm.on(TestState.A, TestEvent.GO)
    def a_to_b(fsm: FSM[TestState, TestEvent, TestData], event: TestEvent) -> TestState:  # pyright: ignore[reportUnusedFunction]
        fsm.data.counter += 1
        return TestState.B

    @fsm.on(TestState.B, TestEvent.BACK)
    def b_to_a(fsm: FSM[TestState, TestEvent, TestData], event: TestEvent) -> TestState:  # pyright: ignore[reportUnusedFunction]
        fsm.data.counter += 1
        return TestState.A

    assert fsm.state == TestState.A
    assert fsm.data.counter == 0

    new_state = fsm.send(TestEvent.GO)
    assert new_state == TestState.B
    assert fsm.state == TestState.B
    assert fsm.data.counter == 1

    new_state = fsm.send(TestEvent.BACK)
    assert new_state == TestState.A
    assert fsm.state == TestState.A
    expected_count = 2
    assert fsm.data.counter == expected_count


def test_missing_handler():
    """Test that missing handlers raise RuntimeError."""
    fsm = FSM[TestState, TestEvent, TestData](
        state=TestState.A,
        data=TestData(),
    )

    with pytest.raises(RuntimeError, match="No handler for"):
        fsm.send(TestEvent.GO)
