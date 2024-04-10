import cv2
import mediapipe as mp
import time
from djitellopy import Tello

# Initialize MediaPipe Hands and Tello drone
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
drone = Tello('192.168.86.22')

# Connect to the drone
drone.connect()
print(f"Battery: {drone.get_battery()}%")

# Connect to the drone's video stream
drone.streamon()

# Define gestures and drone commands
def detect_gesture(landmarks):
    # Gesture detection logic here...
    pass  # Placeholder for the actual gesture detection logic

# Initialize the video capture
cap = cv2.VideoCapture('udp://192.168.86.22:11111')

# Main loop
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to get frame")
            break

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Draw the hand landmarks on the frame
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Display the frame with landmarks
        cv2.imshow('Tello Hand Control', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
drone.end()
