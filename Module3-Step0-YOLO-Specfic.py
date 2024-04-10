import cv2
import torch

# Setup YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Define the object you want to detect - change 'person' to any valid object class (e.g., 'car', 'cat')
object_to_detect = 'apple'

# Start video capture from the default computer's camera
cap = cv2.VideoCapture(0)

while True:
    # Get the current frame from the video capture
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Pass the frame to YOLOv5 for object detection
    results = model(frame_rgb)

    # Filter results for a label that matches the object to detect
    detections = results.pandas().xyxy[0]  # Get detection results as a Pandas DataFrame
    target_detections = detections[detections['name'] == object_to_detect]

    # Display the original frame if no targeted object is detected
    if target_detections.empty:
        cv2.imshow('YOLOv5', frame)
    else:
        # Iterate over detected objects and draw bounding boxes on the frame
        for index, detection in target_detections.iterrows():
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            label = f"{detection['name']} {detection['confidence']:.2f}"
            color = (0, 255, 0)  # Green box for visibility
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Display frame with detected objects
        cv2.imshow('YOLOv5', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
