"""Tests for the FSM implementation."""

from dataclasses import dataclass, field
from enum import Enum, auto

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


SimpleEvent = GoEvent | BackEvent


@dataclass
class SimpleContext:
    counter: int = 0


def test_basic_transition():
    """Test basic state transitions."""
    fsm = FSM[SimpleState, SimpleEvent, SimpleContext](
        state=SimpleState.A,
        context=SimpleContext(),
    )

    @fsm.on(SimpleState.A, GoEvent)
    def _a_to_b(
        fsm: FSM[SimpleState, SimpleEvent, SimpleContext], event: GoEvent
    ) -> SimpleState:
        fsm.context.counter += 1
        return SimpleState.B

    @fsm.on(SimpleState.B, BackEvent)
    def _b_to_a(
        fsm: FSM[SimpleState, SimpleEvent, SimpleContext], event: BackEvent
    ) -> SimpleState:
        fsm.context.counter += 1
        return SimpleState.A

    assert fsm.state == SimpleState.A
    assert fsm.context.counter == 0

    new_state = fsm.send(GoEvent())
    assert new_state == SimpleState.B
    assert fsm.state == SimpleState.B
    assert fsm.context.counter == 1

    new_state = fsm.send(BackEvent())
    assert new_state == SimpleState.A
    assert fsm.state == SimpleState.A
    expected_count = 2
    assert fsm.context.counter == expected_count


def test_missing_handler():
    """Test that missing handlers raise RuntimeError."""
    fsm = FSM[SimpleState, SimpleEvent, SimpleContext](
        state=SimpleState.A,
        context=SimpleContext(),
    )

    with pytest.raises(RuntimeError, match="No handler for"):
        fsm.send(GoEvent())


def test_clone():
    """Test FSM cloning functionality."""
    # Create original FSM
    original = FSM[SimpleState, SimpleEvent, SimpleContext](
        state=SimpleState.A,
        context=SimpleContext(counter=5),
    )

    # Register handlers
    @original.on(SimpleState.A, GoEvent)
    def _a_to_b(
        fsm: FSM[SimpleState, SimpleEvent, SimpleContext], event: GoEvent
    ) -> SimpleState:
        fsm.context.counter += 1
        return SimpleState.B

    # Clone the FSM
    cloned = original.clone()

    # Verify initial state
    assert cloned.state == original.state
    assert cloned.context.counter == original.context.counter
    assert cloned is not original
    assert cloned.context is not original.context

    # Verify handlers are shared
    assert cloned._handlers is original._handlers  # pyright: ignore[reportPrivateUsage]

    # Modify cloned FSM
    cloned.send(GoEvent())

    # Verify independence
    assert cloned.state == SimpleState.B
    assert original.state == SimpleState.A
    assert cloned.context.counter == 6
    assert original.context.counter == 5


def test_clone_with_complex_context():
    """Test cloning with nested data structures in context."""

    @dataclass
    class ComplexContext:
        items: list[str] = field(default_factory=lambda: [])
        metadata: dict[str, int] = field(default_factory=lambda: {})

    # Create FSM with complex context
    original = FSM[SimpleState, SimpleEvent, ComplexContext](
        state=SimpleState.A,
        context=ComplexContext(
            items=["a", "b", "c"], metadata={"count": 10, "score": 20}
        ),
    )

    # Clone it
    cloned = original.clone()

    # Modify cloned context
    cloned.context.items.append("d")
    cloned.context.metadata["count"] = 15

    # Verify original is unaffected
    assert original.context.items == ["a", "b", "c"]
    assert original.context.metadata["count"] == 10

    # Verify cloned has changes
    assert cloned.context.items == ["a", "b", "c", "d"]
    assert cloned.context.metadata["count"] == 15
