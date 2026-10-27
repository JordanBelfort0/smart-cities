import cv2
import numpy as np
from ultralytics import YOLO
from sort import Sort   

model = YOLO("yolov8n.pt")

tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

cap = cv2.VideoCapture("traffic.mp4")

lane1_y = (200, 300)
lane2_y = (300, 400)
lane3_y = (400, 500)

vehicle_positions = {}

vehicle_classes = [2, 3, 5, 7]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1020, 500))

    results = model(frame)[0]

    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        if cls in vehicle_classes and conf > 0.4:
            detections.append([x1, y1, x2, y2, conf])

    detections = np.array(detections)

    tracked_objects = tracker.update(detections)

    lane_counts = [0, 0, 0]
    speeds = []

    for obj in tracked_objects:
        x1, y1, x2, y2, obj_id = map(int, obj)

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        if obj_id in vehicle_positions:
            prev_cx, prev_cy = vehicle_positions[obj_id]
            distance = np.sqrt((cx - prev_cx)**2 + (cy - prev_cy)**2)
            speed = distance  
            speeds.append(speed)
        else:
            speed = 0

        vehicle_positions[obj_id] = (cx, cy)

        if lane1_y[0] < cy < lane1_y[1]:
            lane_counts[0] += 1
            lane_color = (255, 0, 0)
        elif lane2_y[0] < cy < lane2_y[1]:
            lane_counts[1] += 1
            lane_color = (0, 255, 0)
        elif lane3_y[0] < cy < lane3_y[1]:
            lane_counts[2] += 1
            lane_color = (0, 0, 255)
        else:
            lane_color = (255, 255, 255)

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), lane_color, 2)
        cv2.putText(frame, f"ID:{obj_id}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, lane_color, 2)

    total_vehicles = sum(lane_counts)

    avg_speed = np.mean(speeds) if len(speeds) > 0 else 0

    density = total_vehicles / 3  # per lane average

    if density < 5 and avg_speed > 5:
        congestion = "LOW"
        color = (0, 255, 0)
    elif density < 15 and avg_speed > 2:
        congestion = "MEDIUM"
        color = (0, 255, 255)
    else:
        congestion = "HIGH"
        color = (0, 0, 255)

    cv2.line(frame, (0, lane1_y[0]), (1020, lane1_y[0]), (255,0,0), 2)
    cv2.line(frame, (0, lane1_y[1]), (1020, lane1_y[1]), (255,0,0), 2)

    cv2.line(frame, (0, lane2_y[0]), (1020, lane2_y[0]), (0,255,0), 2)
    cv2.line(frame, (0, lane2_y[1]), (1020, lane2_y[1]), (0,255,0), 2)

    cv2.line(frame, (0, lane3_y[0]), (1020, lane3_y[0]), (0,0,255), 2)
    cv2.line(frame, (0, lane3_y[1]), (1020, lane3_y[1]), (0,0,255), 2)


    cv2.putText(frame, f"Lane1: {lane_counts[0]}", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)

    cv2.putText(frame, f"Lane2: {lane_counts[1]}", (20,70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.putText(frame, f"Lane3: {lane_counts[2]}", (20,100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.putText(frame, f"Total: {total_vehicles}", (20,140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.putText(frame, f"Avg Speed: {avg_speed:.2f}", (20,180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    cv2.putText(frame, f"Traffic: {congestion}", (20,220),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    cv2.imshow("Advanced Traffic System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
