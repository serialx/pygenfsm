"""A minimal, clean, typed and synchronous FSM implementation inspired by Erlang's gen_fsm."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Generic,
    Protocol,
    TypeVar,
    Union,
    cast,
)

# --- type parameters ---------------------------------------------------------

S = TypeVar("S", bound=Enum)  # State enum  (e.g. LightState)
E = TypeVar("E")  # Event type  (e.g. LightEvent enum or complex event class)
D = TypeVar("D")  # Arbitrary user data

# --- handler protocol --------------------------------------------------------


# Event handler type - we use TypeVar to allow handlers to accept
# specific event types that are part of a union
EventType = TypeVar("EventType")


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
    _handlers: dict[tuple[S, Any], Handler[S, E, D]] = field(default_factory=lambda: {})

    # ――― decorator for registering handlers ―――
    def on(
        self, state: S, event_type: Union[E, type[Any]]
    ) -> Callable[[Callable[[FSM[S, E, D], Any], S]], Callable[[FSM[S, E, D], Any], S]]:
        """Register a handler for a state/event combination.

        Usage:
        ```python
        # With enum events:
        @fsm.on(State.ON, Event.TOGGLE)
        def turn_off(fsm, evt): ...

        # With complex events:
        @fsm.on(State.CONNECTING, ConnectionErrorEvent)
        def handle_error(fsm, evt): ...
        ```
        """

        def decorator(
            fn: Callable[[FSM[S, E, D], Any], S],
        ) -> Callable[[FSM[S, E, D], Any], S]:
            # For enum events, store by value; for others, by type
            if isinstance(event_type, Enum):
                key = (state, event_type)
            else:
                key = (state, event_type)
            self._handlers[key] = cast(Handler[S, E, D], fn)
            return fn

        return decorator

    # ――― event dispatcher ―――
    def send(self, event: E) -> S:
        """Send an event to the FSM and transition to the next state."""
        # For enum events, look up by value; for others, by type
        if isinstance(event, Enum):
            key = (self.state, event)
        else:
            key = (self.state, type(event))

        try:
            handler = self._handlers[key]
        except KeyError as e:
            event_repr = event if isinstance(event, Enum) else type(event).__name__
            msg = f"No handler for ({self.state}, {event_repr})"
            raise RuntimeError(msg) from e
        self.state = handler(self, event)  # may mutate self.data
        return self.state
