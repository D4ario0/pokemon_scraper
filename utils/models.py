from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Stats:
    HP: int
    ATA: int
    DEF: int
    SPA: int
    SPD: int
    SPE: int
    BST: int


@dataclass
class Pokemon:
    name: str
    dex_number: int = field(init=False)
    primary_type: int = field(init=False)
    secondary_type: Optional[int] = field(init=False)
    height: float = field(init=False)
    weight: Optional[float] = field(init=False)
    abilities: list[str] = field(init=False)
    hidden_ability: Optional[str] = field(init=False)
    EV_yield: str = field(init=False)
    catch_rate: int = field(init=False)
    base_friendship: int = field(init=False)
    growth_rate: str = field(init=False)
    primary_egg_group: int = field(init=False)
    secondary_egg_group: Optional[int] = field(init=False)
    egg_cycles: int = field(init=False)
    stats: Stats = field(init=False)
    tags: list[str] = field(init=False)

