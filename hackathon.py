import cv2
import numpy as np
import requests
import time
import threading

# Firebase URL - Isme '.json' last mein zaroori hai
DB_URL = "https://hackathon-project-333b5-default-rtdb.firebaseio.com/live_monitoring.json"

def send_to_cloud(event_type, status_text):
    # Ye function har alert ko ek naya "Node" (line) bana kar bhejega
    data = {
        'timestamp': time.strftime("%H:%M:%S"),
        'event': event_type,
        'status': status_text,
        'location': 'KITS_NAGPUR_GATE_01'
    }
    try:
        # POST karne se data ek ke niche ek judta hai (Terminal ki tarah)
        requests.post(DB_URL, json=data)
        print(f"Logged to Firebase: {event_type}")
    except:
        pass

cap = cv2.VideoCapture(0)
ret, frame1 = cap.read()
ret, frame2 = cap.read()
last_sync = 0

while cap.isOpened():
    # --- MOTION LOGIC ---
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(cv2.dilate(thresh, None, iterations=3), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
    
    # --- COLOR RANGES ---
    # Weapon (Blue)
    weapon_mask = cv2.inRange(hsv, np.array([90, 100, 100]), np.array([135, 255, 255]))
    # Fire (Yellow/Orange)
    fire_mask = cv2.inRange(hsv, np.array([5, 100, 100]), np.array([40, 255, 255]))

    status = "Monitoring..."
    event_detected = None
    color = (0, 255, 0)

    # --- DETECTION LOGIC ---
    if cv2.countNonZero(weapon_mask) > 1000:
        status, event_detected, color = "ALERT: SIMULATED WEAPON", "WEAPON", (255, 0, 0)
    elif cv2.countNonZero(fire_mask) > 1500:
        status, event_detected, color = "ALERT: FIRE DETECTED", "FIRE", (0, 165, 255)
    else:
        for contour in contours:
            if cv2.contourArea(contour) > 10000:
                status, event_detected, color = "MOTION DETECTED", "MOTION", (255, 255, 255)

    # Cloud Sync (Har 3-4 second mein agar koi event hai)
    if event_detected and (time.time() - last_sync > 3):
        threading.Thread(target=send_to_cloud, args=(event_detected, status)).start()
        last_sync = time.time()

    # Screen UI
    cv2.rectangle(frame1, (0, 0), (640, 60), (0, 0, 0), -1)
    cv2.putText(frame1, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.imshow("Rakshak AI - Live Feed", frame1)
    
    frame1 = frame2
    ret, frame2 = cap.read()
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()