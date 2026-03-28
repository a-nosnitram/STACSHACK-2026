import asyncio

# for sending messages from game to vision
game_to_vision: asyncio.Queue = asyncio.Queue()
# for sending messages from vision to game
vision_to_game: asyncio.Queue = asyncio.Queue()

"""
Game -> vision
{"type": "start_match", "poses": ["squat", "kick", "jab"], "round_ms": 3000}

{"type": "stop_match"}


Vision -> game
{"type": "round_result", "round": 1, "pose": "squat", "winner": 0, "scores": {"0": 0.11, "1": 0.19}}

{"type": "match_complete", "wins": {"0": 3, "1": 2}}

"""
