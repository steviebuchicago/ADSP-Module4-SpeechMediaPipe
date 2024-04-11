
import cv2
import torch
from djitellopy import Tello
import math
import time

# Initialize Tello drone
tello = Tello('192.168.87.29')
tello.connect()
print(f'Battery Life Percentage: {tello.get_battery()}%')  # Display battery level
tello.streamon()

# Load the YOLO model and wait for it to initialize fully
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
print("YOLO model loaded. Waiting for stabilization...")
time.sleep(10)  # Wait for 10 seconds to stabilize everything

# Define the target object and constants
target_object = 'person'
TARGET_SIZE = 100  # Adjust based on actual requirements
KP_DISTANCE = 0.1
KP_POSITION = 0.1
MIN_MOVE_DISTANCE = 30

def adjust_drone_position(person_width, center_x, center_y, frame_width, frame_height):
    """
    Adjust drone's position based on detected person's size and position.
    """
    # Distance adjustment with minimum move enforcement
    error_distance = person_width - TARGET_SIZE
    distance_command = max(int(KP_DISTANCE * abs(error_distance)), MIN_MOVE_DISTANCE)

    if error_distance > 0:
        tello.move_back(distance_command)
    elif error_distance < 0:
        tello.move_forward(distance_command)

    # Lateral position adjustment
    error_x = center_x - frame_width // 2
    if abs(error_x) > 20:
        lateral_command = max(int(KP_POSITION * abs(error_x)), MIN_MOVE_DISTANCE)
        if error_x > 0:
            tello.move_right(lateral_command)
        else:
            tello.move_left(lateral_command)

    # Vertical position adjustment
    error_y = center_y - frame_height // 2
    if abs(error_y) > 20:
        vertical_command = max(int(KP_POSITION * abs(error_y)), MIN_MOVE_DISTANCE)
        if error_y > 0:
            tello.move_down(vertical_command)
        else:
            tello.move_up(vertical_command)

tello.takeoff()  # Drone takes off

try:
    while True:
        frame = tello.get_frame_read().frame
        results = model(frame)

        for *xyxy, conf, cls in reversed(results.xyxy[0]):
            if model.names[int(cls)] == target_object:
                x1, y1, x2, y2 = map(int, xyxy)
                person_width = x2 - x1
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

                # Draw rectangle and label around the detected person
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'{model.names[int(cls)]} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                adjust_drone_position(person_width, center_x, center_y, frame.shape[1], frame.shape[0])
                break  # Focus on the first detected person

        cv2.imshow("Drone's View", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()
