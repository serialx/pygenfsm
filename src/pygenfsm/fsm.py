"""A minimal, clean, typed and synchronous FSM implementation inspired by Erlang's gen_fsm."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Callable,
    Generic,
    Protocol,
    TypeVar,
)

# --- type parameters ---------------------------------------------------------

S = TypeVar("S", bound=Enum)  # State enum  (e.g. LightState)
E = TypeVar("E", bound=Enum)  # Event enum  (e.g. LightEvent)
D = TypeVar("D")  # Arbitrary user data

# --- handler protocol --------------------------------------------------------


class Handler(Protocol[S, E, D]):
    """A state-transition handler.

    Returns the *next* state after handling `event` and (optionally) mutating
    `fsm.data`.
    """

    def __call__(self, fsm: FSM[S, E, D], event: E) -> S:
        """Handle the state transition."""
        ...


# --- the FSM core ------------------------------------------------------------


@dataclass
class FSM(Generic[S, E, D]):
    """Minimal synchronous FSM (a Pythonic `gen_fsm`)."""

    state: S
    data: D
    _handlers: dict[tuple[S, E], Handler[S, E, D]] = field(default_factory=dict)

    # ――― decorator for registering handlers ―――
    def on(self, state: S, event: E) -> Callable[[Handler[S, E, D]], Handler[S, E, D]]:
        """Register a handler for a state/event combination.

        Usage:
        ```python
        @fsm.on(State.ON, Event.TOGGLE)
        def turn_off(fsm, evt): ...
        ```
        """

        def decorator(fn: Handler[S, E, D]) -> Handler[S, E, D]:
            self._handlers[(state, event)] = fn
            return fn

        return decorator

    # ――― event dispatcher ―――
    def send(self, event: E) -> S:
        """Send an event to the FSM and transition to the next state."""
        key = (self.state, event)
        try:
            handler = self._handlers[key]
        except KeyError as e:
            msg = f"No handler for ({self.state}, {event})"
            raise RuntimeError(msg) from e
        self.state = handler(self, event)  # may mutate self.data
        return self.state
