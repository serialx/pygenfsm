"""Example: A toggle light-switch using the FSM."""

from dataclasses import dataclass
from enum import Enum, auto

from pygenfsm import FSM


class LightState(Enum):
    OFF = auto()
    ON = auto()


@dataclass
class ToggleEvent:
    pass


# Shared mutable data (totally optional)
@dataclass
class LightContext:
    toggles: int = 0


# Type alias for cleaner code
LightFSM = FSM[LightState, ToggleEvent, LightContext]

# Build the FSM ---------------------------------------------------------------
fsm = LightFSM(
    state=LightState.OFF,
    context=LightContext(),
)


@fsm.on(LightState.OFF, ToggleEvent)
def turn_on(fsm: LightFSM, event: ToggleEvent) -> LightState:
    fsm.context.toggles += 1
    print("💡  switched ON")
    return LightState.ON


@fsm.on(LightState.ON, ToggleEvent)
def turn_off(fsm: LightFSM, event: ToggleEvent) -> LightState:
    fsm.context.toggles += 1
    print("💡  switched OFF")
    return LightState.OFF


# Drive it -------------------------------------------------------------------
if __name__ == "__main__":
    for _ in range(3):
        fsm.send(ToggleEvent())

    print("Total toggles:", fsm.context.toggles)
