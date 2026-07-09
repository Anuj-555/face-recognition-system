import os
import face_recognition
import pickle
import json
from datetime import datetime

from database.db import get_connection


# =========================
# Load Model
# =========================
if os.path.exists("models/encodings.pickle"):

    print("Loading encodings...")

    with open("models/encodings.pickle", "rb") as f:
        data = pickle.load(f)

    print("Encodings loaded successfully.")

else:

    data = {
        "encodings": [],
        "names": [],
        "ids": []
    }


# =========================
# Recognize Frame
# =========================
def recognize_frame(rgb_frame):

    if len(data["encodings"]) == 0:
        return {
            "success": False,
            "message": "Model not trained."
        }

    boxes = face_recognition.face_locations(rgb_frame)

    encodings = face_recognition.face_encodings(
        rgb_frame,
        boxes
    )

    if len(encodings) == 0:
        return {
            "success": False,
            "message": "No face detected."
        }

    conn = get_connection()
    cursor = conn.cursor()

    for encoding in encodings:

        face_distances = face_recognition.face_distance(
            data["encodings"],
            encoding
        )

        best_match_index = face_distances.argmin()

        if face_distances[best_match_index] < 0.50:

            name = data["names"][best_match_index]
            user_id = data["ids"][best_match_index]

            now = datetime.now()

            attendance_date = now.date()
            attendance_time = now.strftime("%H:%M:%S")

            cursor.execute(
                """
                SELECT id
                FROM attendance
                WHERE name=%s
                AND date=%s
                """,
                (
                    name,
                    attendance_date
                )
            )

            existing = cursor.fetchone()

            if not existing:

                cursor.execute(
                    """
                    INSERT INTO attendance(name,date,time)
                    VALUES(%s,%s,%s)
                    """,
                    (
                        name,
                        attendance_date,
                        attendance_time
                    )
                )

                conn.commit()

            result = {
                "id": user_id,
                "name": name,
                "date": str(attendance_date),
                "time": attendance_time
            }

            with open(
                "last_recognition.json",
                "w"
            ) as file:
                json.dump(
                    result,
                    file,
                    indent=4
                )

            cursor.close()
            conn.close()

            return {
                "success": True,
                "recognized": True,
                "name": name,
                "date": str(attendance_date),
                "time": attendance_time
            }

    cursor.close()
    conn.close()

    return {
        "success": True,
        "recognized": False,
        "message": "Unknown face."
    }