import cv2
import face_recognition
import pickle
import json

from database.db import get_connection
from datetime import datetime

print("Loading encodings...")

# Load trained model
with open("models/encodings.pickle", "rb") as f:
    data = pickle.load(f)

print("Encodings loaded successfully.")

# Open webcam
video = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not video.isOpened():
    print("Camera not working!")
    exit()

# Database connection
conn = get_connection()
cursor = conn.cursor()

marked_users = set()

while True:

    ret, frame = video.read()

    if not ret:
        print("Failed to grab frame")
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding, box in zip(encodings, boxes):

        name = "Unknown"

        if len(data["encodings"]) > 0:

            face_distances = face_recognition.face_distance(
                data["encodings"], encoding
            )

            best_match_index = face_distances.argmin()

            # Lower distance = better match
            if face_distances[best_match_index] < 0.50:

                name = data["names"][best_match_index]
                user_id = data["ids"][best_match_index]

                if user_id not in marked_users:

                    now = datetime.now()

                    date = now.date()
                    time = now.strftime("%H:%M:%S")

                    cursor.execute(
                        """
                        INSERT INTO attendance(name, date, time)
                        VALUES(%s,%s,%s)
                        """,
                        (name, date, time),
                    )

                    conn.commit()

                    marked_users.add(user_id)

                    result = {
                        "id": user_id,
                        "name": name,
                        "date": str(date),
                        "time": time,
                    }

                    with open("last_recognition.json", "w") as file:
                        json.dump(result, file, indent=4)

                    print(f"Attendance marked for {name}")

        top, right, bottom, left = box

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.putText(
            frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()

cursor.close()
conn.close()

print("System closed.")