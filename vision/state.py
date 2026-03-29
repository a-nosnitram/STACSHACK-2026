import numpy as np
from typing import Dict, List, Optional

# this is our frame state that we're reading from
# int: The unique client ID of the phone.
# np.ndarray: The latest decoded video frame.
clients: Dict[int, np.ndarray] = {}

ui_state = {
    "countdown_active": False,
    "countdown_start_ms": 0,
    "saved_banner_active": False,
    "saved_banner_until_ms": 0,
    "saved_banner_text": "",
    "saved_banner_color": (0, 255, 0),
    "recognition_active": False,
}


class MatchState:
    def __init__(self):
        self.poses: List[str] = []
        self.round_ms: int = 10000
        self.prep_ms: int = 10000
        self.hold_ms: int = 5000
        self.round_index: int = 0
        self.round_start_ms: int = 0
        self.match_active: bool = False
        self.total_scores: Dict[int, float] = {}
        self.sample_counts: Dict[int, int] = {}
        self.awaiting_players: bool = False
        self.expected_players: int = 2

    def handle_message(self, msg: dict, now_ms: int):
        if msg["type"] == "start_match":
            self.poses = list(msg["poses"])
            self.round_ms = int(
                msg.get("rounds_ms", msg.get("round_ms", 7000)))
            self.prep_ms = self.round_ms
            self.hold_ms = self.round_ms
            self.round_index = 0
            self.round_start_ms = now_ms
            self.match_active = True
            self.awaiting_players = True
            self.total_scores = {}
            self.sample_counts = {}
            ui_state["recognition_active"] = False
            print(f"Starting match with poses: {self.poses}")
            print(f"Prep: {self.prep_ms} ms, Hold: {self.hold_ms} ms")

        # elif msg["type"] == "stop_match":
        #     print("Stopping match")
        #     self.match_active = False
        #     self.awaiting_players = False
        #     ui_state["recognition_active"] = False


match = MatchState()
