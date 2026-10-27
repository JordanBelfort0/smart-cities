import os
import random
import time
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

image_folder = "images"
output_folder = "outputnew"
os.makedirs(output_folder, exist_ok=True)

REAL_CYCLE = 60
DEMO_CYCLE = 12
SCALE = DEMO_CYCLE / REAL_CYCLE

VEHICLES = ["car", "truck", "bus", "motorbike"]

# ---------------- MAIN LOOP ----------------
while True:

    print("\n==============================")
    print("🚦 NEW TRAFFIC CYCLE STARTED")
    print("==============================\n")

    images = [img for img in os.listdir(image_folder) if img.endswith(('.jpg', '.png'))]

    # Select 4 random images
    selected = random.sample(images, 4)

    print("Selected Images:")
    for i, img in enumerate(selected):
        print(f"Lane_{i+1}: {img}")

    lane_counts = {}
    lane_images = {}

    # -------- PROCESS EACH LANE --------
    for i, img_name in enumerate(selected):
        lane = f"Lane_{i+1}"
        path = os.path.join(image_folder, img_name)

        image = cv2.imread(path)
        results = model(image)

        vehicle_count = 0

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]

                if label in VEHICLES:
                    vehicle_count += 1

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Draw bounding box
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Label
                    cv2.putText(image, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        lane_counts[lane] = vehicle_count
        lane_images[lane] = image

    # -------- COMPUTE TIMING --------
    total_vehicles = sum(lane_counts.values())
    lane_times = {}

    print("\nLane Analysis:")

    for lane, count in lane_counts.items():
        if total_vehicles == 0:
            time_alloc = 2
        else:
            time_alloc = int((count / total_vehicles) * REAL_CYCLE * SCALE)
            time_alloc = max(2, time_alloc)  # minimum 2 sec

        lane_times[lane] = time_alloc

        print(f"{lane}: {count} vehicles → {time_alloc}s")

    # -------- SAVE IMAGES WITH TIME --------
    timestamp = int(time.time())

    for lane in lane_images:
        img = lane_images[lane]

        # Overlay info
        cv2.putText(img, f"{lane}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        cv2.putText(img, f"Vehicles: {lane_counts[lane]}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(img, f"Time: {lane_times[lane]}s", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        out_path = os.path.join(output_folder, f"{lane}_{timestamp}.jpg")
        cv2.imwrite(out_path, img)

    # -------- SIGNAL SEQUENCE --------
    print("\n🚦 SIGNAL SEQUENCE START\n")

    for lane, t in lane_times.items():
        print(f">>> {lane} GREEN for {t}s <<<")
        time.sleep(t)

    print("\n🔁 CYCLE COMPLETE — RESELECTING LANES...\n")
    time.sleep(1)
