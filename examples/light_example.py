"""Example: A toggle light-switch using the FSM."""

from dataclasses import dataclass
from enum import Enum, auto

from pygenfsm import FSM


class LightState(Enum):
    OFF = auto()
    ON = auto()


class LightEvent(Enum):
    TOGGLE = auto()


# Shared mutable data (totally optional)
@dataclass
class LightData:
    toggles: int = 0


# Build the FSM ---------------------------------------------------------------
fsm = FSM[LightState, LightEvent, LightData](
    state=LightState.OFF,
    data=LightData(),
)


@fsm.on(LightState.OFF, LightEvent.TOGGLE)
def turn_on(
    fsm: FSM[LightState, LightEvent, LightData], event: LightEvent
) -> LightState:
    fsm.data.toggles += 1
    print("💡  switched ON")
    return LightState.ON


@fsm.on(LightState.ON, LightEvent.TOGGLE)
def turn_off(
    fsm: FSM[LightState, LightEvent, LightData], event: LightEvent
) -> LightState:
    fsm.data.toggles += 1
    print("💡  switched OFF")
    return LightState.OFF


# Drive it -------------------------------------------------------------------
if __name__ == "__main__":
    for _ in range(3):
        fsm.send(LightEvent.TOGGLE)

    print("Total toggles:", fsm.data.toggles)
