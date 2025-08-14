import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLO model once, to avoid repeated loading on each request
model = YOLO("yolov8n.pt")

# Vehicle classes and their weights (importance)
VEHICLE_CLASSES = ['car', 'motorcycle', 'truck', 'bicycle', 'bus']

vehicle_weights = {
    'car': 1,
    'motorcycle': 0.5,
    'truck': 2,
    'bicycle': 0.3,
    'bus': 2
}

# Passage capacity: higher means more vehicles of this type can pass simultaneously, reducing wait time
vehicle_passage_capacity = {
    'car': 1.0,
    'motorcycle': 1.5,
    'truck': 0.5,
    'bicycle': 1.2,
    'bus': 0.4
}

MIN_GREEN = 5
MAX_GREEN = 40
lanes = ['North', 'East', 'South', 'West']

current_lane_index = 0
green_time_remaining = 0

def count_vehicles_by_type_yolo(frame):
    results = model(frame)
    counts = {v: 0 for v in VEHICLE_CLASSES}
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        cls_name = model.model.names[cls_id]
        if cls_name in VEHICLE_CLASSES:
            counts[cls_name] += 1
    return counts

def assign_green_time_weighted(vehicle_counts):
    effective_vehicle_load = 0
    for vehicle_type, count in vehicle_counts.items():
        weight = vehicle_weights.get(vehicle_type, 1)
        passage_capacity = vehicle_passage_capacity.get(vehicle_type, 1.0)

        # Adjust count by dividing by passage capacity 
        adjusted_count = count * weight / passage_capacity
        effective_vehicle_load += adjusted_count

    if effective_vehicle_load == 0:
        return MIN_GREEN

    # Cap max scaled count to 20 for scaling
    scaling_factor = min(effective_vehicle_load, 20) / 20
    time_for_lane = int(MIN_GREEN + (MAX_GREEN - MIN_GREEN) * scaling_factor)
    return min(MAX_GREEN, max(MIN_GREEN, time_for_lane))

def process_frame_for_lane(frame, lane_name):
    global current_lane_index, green_time_remaining, lanes

    if lane_name not in lanes:
        lane_name = lanes[current_lane_index]

    current_lane_index = lanes.index(lane_name)

    vehicle_counts = count_vehicles_by_type_yolo(frame)
    green_time = assign_green_time_weighted(vehicle_counts)

    green_time_remaining = green_time

    return {
        "lane": lane_name,
        "vehicle_count": sum(vehicle_counts.values()),
        "green_time": green_time,
        "vehicle_counts": vehicle_counts  # Optional: you can use detailed counts in frontend if needed
    }
