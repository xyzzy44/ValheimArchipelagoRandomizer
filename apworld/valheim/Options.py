import typing
from dataclasses import dataclass
from functools import cached_property

from Options import (
    Choice,
    Range,
    DeathLink,
    Toggle,
    DefaultOnToggle,
    StartInventoryPool,
    ItemDict,
    PerGameCommonOptions,
)

class Goal(Choice):
    """Boss Trophy required to goal.
    Eikthyr: Eikthyr
    TheElder: The Elder
    Bonemass: Bonemass
    Moder: Moder
    Yagluth: Yagluth
    Queen: Queen
    Fader: Fader"""


    auto_display_name = False
    display_name = "Goal Boss"
    option_Eikthyr = 0
    option_TheElder = 1
    option_Bonemass = 2
    option_Moder = 3
    option_Yagluth = 4
    option_Queen = 5
    option_Fader = 6

@dataclass
class ValheimOptions(PerGameCommonOptions):
    goal: Goal
