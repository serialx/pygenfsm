"""Example: A toggle light-switch using the async FSM."""

import asyncio
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
async def turn_on(fsm: LightFSM, event: ToggleEvent) -> LightState:
    fsm.context.toggles += 1
    print("💡  switched ON")
    # Simulate async operation (e.g., sending command to hardware)
    await asyncio.sleep(0.1)
    return LightState.ON


@fsm.on(LightState.ON, ToggleEvent)
async def turn_off(fsm: LightFSM, event: ToggleEvent) -> LightState:
    fsm.context.toggles += 1
    print("💡  switched OFF")
    # Simulate async operation
    await asyncio.sleep(0.1)
    return LightState.OFF


# Drive it -------------------------------------------------------------------
async def main():
    """Run the light switch FSM demo."""
    for _ in range(3):
        await fsm.send(ToggleEvent())

    print("Total toggles:", fsm.context.toggles)


if __name__ == "__main__":
    asyncio.run(main())
