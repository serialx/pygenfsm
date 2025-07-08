"""A minimal, clean, typed and synchronous FSM implementation inspired by Erlang's gen_fsm."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    cast,
)

# --- type parameters ---------------------------------------------------------

S = TypeVar("S", bound=Enum)  # State enum  (e.g. LightState)
E = TypeVar("E")  # Event type  (must be a dataclass)
C = TypeVar("C")  # Arbitrary user data

# --- handler protocol --------------------------------------------------------


# Event handler type - we use TypeVar to allow handlers to accept
# specific event types that are part of a union
SpecificEventType = TypeVar("SpecificEventType")


class Handler(Protocol[S, E, C]):
    """A state-transition handler.

    Returns the *next* state after handling `event` and (optionally) mutating
    `fsm.data`.
    """

    def __call__(self, fsm: FSM[S, E, C], event: E) -> S:
        """Handle the state transition."""
        ...


# --- the FSM core ------------------------------------------------------------


@dataclass
class FSM(Generic[S, E, C]):
    """Minimal synchronous FSM (a Pythonic `gen_fsm`)."""

    state: S
    context: C
    _handlers: dict[tuple[S, Any], Handler[S, E, C]] = field(default_factory=lambda: {})

    # ――― decorator for registering handlers ―――
    def on(
        self, state: S, event_type: type[SpecificEventType]
    ) -> Callable[
        [Callable[[FSM[S, E, C], SpecificEventType], S]],
        Callable[[FSM[S, E, C], SpecificEventType], S],
    ]:
        """Register a handler for a state/event combination.

        Usage:
        ```python
        @fsm.on(State.CONNECTING, ConnectionErrorEvent)
        def handle_error(fsm, evt): ...
        ```
        """

        def decorator(
            fn: Callable[[FSM[S, E, C], SpecificEventType], S],
        ) -> Callable[[FSM[S, E, C], SpecificEventType], S]:
            key = (state, event_type)
            self._handlers[key] = cast(Handler[S, E, C], fn)
            return fn

        return decorator

    # ――― event dispatcher ―――
    def send(self, event: E) -> S:
        """Send an event to the FSM and transition to the next state."""
        key = (self.state, type(event))

        try:
            handler = self._handlers[key]
        except KeyError as e:
            event_repr = type(event).__name__
            msg = f"No handler for ({self.state}, {event_repr})"
            raise RuntimeError(msg) from e
        self.state = handler(self, event)  # may mutate self.data
        return self.state

    # ――― cloning ―――
    def clone(self) -> FSM[S, E, C]:
        """Create a deep copy of the FSM instance.

        Returns a new FSM instance with:
        - The same current state
        - A deep copy of the context
        - The same handlers (handlers are shared, not copied)

        This is useful for creating independent FSM instances that share
        the same behavior but have separate state and context.
        """
        return FSM(
            state=self.state,
            context=deepcopy(self.context),
            _handlers=self._handlers,  # Share handlers
        )
