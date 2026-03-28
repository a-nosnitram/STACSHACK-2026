import numpy as np

# this is our frame state that we're reading from
# int: The unique client ID of the phone.
# np.ndarray: The latest decoded video frame.
clients: dict[int, np.ndarray] = {}

ui_state = {
    "countdown_active": False,
    "countdown_start_ms": 0,
    "saved_banner_active": False,
    "saved_banner_until_ms": 0,
    "saved_banner_text": "",
    "saved_banner_color": (0, 255, 0),
}
