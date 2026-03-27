from dataclasses import dataclass
from typing import Dict

from ..pose.pose_defs import PoseName


@dataclass
class Attack:
    name: str
    damage: int
    cooldown_ms: int


POSE_TO_ATTACK: Dict[PoseName, Attack] = {
    PoseName.PUNCH: Attack(name="Punch", damage=5, cooldown_ms=300),
    PoseName.KICK: Attack(name="Kick", damage=8, cooldown_ms=500),
    PoseName.SLASH: Attack(name="Slash", damage=10, cooldown_ms=700),
}
