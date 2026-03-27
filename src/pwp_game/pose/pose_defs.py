from dataclasses import dataclass
from enum import Enum
from typing import List


class PoseName(str, Enum):
    IDLE = "idle"
    PUNCH = "punch"
    KICK = "kick"
    SLASH = "slash"
    UNKNOWN = "unknown"


@dataclass
class PoseDefinition:
    name: PoseName
    description: str
    reference_keypoints: List[int]


DEFAULT_POSES: List[PoseDefinition] = [
    PoseDefinition(PoseName.PUNCH, "Right hand forward", [16, 14, 12]),
    PoseDefinition(PoseName.KICK, "Right leg forward", [28, 26, 24]),
    PoseDefinition(PoseName.SLASH, "Both hands raised", [15, 16, 11, 12]),
]
