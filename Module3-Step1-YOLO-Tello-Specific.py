import cv2
import torch
import time
from djitellopy import Tello

# Initialize and connect the Tello drone
tello = Tello('192.168.87.31')
tello.connect()

# Start video streaming
tello.streamon()

# Setup YOLOv5 for object detection
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Define the target object type to track
target_object = 'person'  # Change this to track different objects

# Constants for drone control based on the object's size and center position
OBJECT_TARGET_AREA = 3000  # Adjust based on trial to maintain 2 feet distance
OBJECT_CENTER_TOLERANCE = 50  # Pixel tolerance for centering
FRAME_CENTER = (480, 360)  # Assuming 960x720 resolution for simplicity

#sleep(10)
#tello.takeoff()

while True:
    frame = tello.get_frame_read().frame
    if frame is None:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb)

    # Filter detections for the target object
    detections = results.pandas().xyxy[0]
    target_detections = detections[detections['name'] == target_object]

    # Calculate area for each detection and find the largest one
    if not target_detections.empty:
        target_detections['area'] = (target_detections['xmax'] - target_detections['xmin']) * (target_detections['ymax'] - target_detections['ymin'])
        largest_detection = target_detections.loc[target_detections['area'].idxmax()]

        object_area = largest_detection['area']
        object_x_center = (largest_detection['xmin'] + largest_detection['xmax']) / 2
        object_y_center = (largest_detection['ymin'] + largest_detection['ymax']) / 2

        # Adjust drone's position to center the object
        if object_x_center < FRAME_CENTER[0] - OBJECT_CENTER_TOLERANCE:
            tello.move_left(20)
        elif object_x_center > FRAME_CENTER[0] + OBJECT_CENTER_TOLERANCE:
            tello.move_right(20)

        if object_y_center < FRAME_CENTER[1] - OBJECT_CENTER_TOLERANCE:
            tello.move_up(20)
        elif object_y_center > FRAME_CENTER[1] + OBJECT_CENTER_TOLERANCE:
            tello.move_down(20)

        # Adjust drone's distance to maintain desired following distance
        if object_area > OBJECT_TARGET_AREA:
            tello.move_back(20)
        elif object_area < OBJECT_TARGET_AREA:
            tello.move_forward(20)

    rendered_frame = results.render()[0]
    rendered_frame_bgr = cv2.cvtColor(rendered_frame, cv2.COLOR_RGB2BGR)
    cv2.imshow('YOLOv5 Tello Detection', rendered_frame_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
tello.streamoff()
cv2.destroyAllWindows()
tello.land()
