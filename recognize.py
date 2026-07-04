import cv2
import face_recognition
import pickle
from database.db import get_connection
from datetime import datetime

print("Loading encodings...")

# Load trained encodings
with open("models/encodings.pickle", "rb") as f:
    data = pickle.load(f)

print("Encodings loaded successfully.")

# Start webcam
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Camera not working!")
    exit()

# Database connection
conn = get_connection()
cursor = conn.cursor()

marked_users = set()  # Prevent duplicate attendance

while True:
    ret, frame = video.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding, box in zip(encodings, boxes):

        matches = face_recognition.compare_faces(data["encodings"], encoding)
        face_distances = face_recognition.face_distance(data["encodings"], encoding)

        name = "Unknown"

        if len(face_distances) > 0:
            best_match_index = face_distances.argmin()

            if matches[best_match_index]:
                name = data["names"][best_match_index]

                if name not in marked_users:
                    now = datetime.now()
                    date = now.date()
                    time = now.time()

                    query = """
                        INSERT INTO attendance (name, date, time)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query, (name, date, time))
                    conn.commit()

                    marked_users.add(name)
                    print(f"Attendance marked for {name}")

        # Draw rectangle
        top, right, bottom, left = box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Put name
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Face Recognition", frame)

    # Press ESC to exit
    if cv2.waitKey(1) == 27:
        break

video.release()
cv2.destroyAllWindows()
conn.close()

print("System closed.")