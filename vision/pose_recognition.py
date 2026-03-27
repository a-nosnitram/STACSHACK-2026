import cv2


# save a pose
def save_pose(pose_landmarks, pose_name):
    with open(f"../poses/{pose_name}.txt", "w") as f:
        for landmark in pose_landmarks.landmark:
            f.write(f"{landmark.x} {landmark.y} {landmark.z}\n")


# recognise a pose from landmarks
