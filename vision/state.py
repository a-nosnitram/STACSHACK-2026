import numpy as np

# this is our frame state that we're reading from
# int: The unique client ID of the phone.
# np.ndarray: The latest decoded video frame.
clients: dict[int, np.ndarray] = {}
