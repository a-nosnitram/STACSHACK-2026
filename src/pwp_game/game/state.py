from dataclasses import dataclass, field
from typing import List

from ..pose.pose_defs import PoseName


@dataclass
class PlayerState:
    health: int = 100
    last_pose: PoseName = PoseName.IDLE
    last_attack_time: float = 0.0


@dataclass
class GameState:
    players: List[PlayerState] = field(default_factory=lambda: [PlayerState(), PlayerState()])
