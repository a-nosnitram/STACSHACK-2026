import time
from typing import Optional

from .attacks import POSE_TO_ATTACK
from .state import GameState
from ..pose.pose_defs import PoseName


class GameEngine:
    def __init__(self) -> None:
        self.state = GameState()

    def apply_pose(self, player_id: int, pose_name: PoseName) -> Optional[str]:
        player = self.state.players[player_id]
        player.last_pose = pose_name

        attack = POSE_TO_ATTACK.get(pose_name)
        if attack is None:
            return None

        now = time.time() * 1000
        if now - player.last_attack_time < attack.cooldown_ms:
            return None

        player.last_attack_time = now
        target_id = 1 - player_id
        self.state.players[target_id].health = max(
            0, self.state.players[target_id].health - attack.damage
        )
        return attack.name
