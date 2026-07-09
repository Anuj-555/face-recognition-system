from flask import Flask, render_template, redirect, request, jsonify
import os
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import date

from database.db import get_connection
from recognize import recognize_frame

app = Flask(__name__)


# =========================
# Home Page
# =========================
@app.route("/")
def home():

    recognition = None

    if os.path.exists("last_recognition.json"):
        with open("last_recognition.json", "r") as file:
            recognition = json.load(file)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) AS total_users FROM users"
    )
    total_users = cursor.fetchone()["total_users"]

    cursor.execute(
        "SELECT COUNT(*) AS total_attendance FROM attendance"
    )
    total_attendance = cursor.fetchone()["total_attendance"]

    cursor.execute(
        """
        SELECT COUNT(*) AS today_attendance
        FROM attendance
        WHERE date=%s
        """,
        (date.today(),)
    )

    today_attendance = cursor.fetchone()["today_attendance"]

    cursor.close()
    conn.close()

    model_status = "Ready"

    if not os.path.exists("models/encodings.pickle"):
        model_status = "Not Trained"

    return render_template(
        "index.html",
        recognition=recognition,
        total_users=total_users,
        total_attendance=total_attendance,
        today_attendance=today_attendance,
        model_status=model_status
    )


# =========================
# Register User
# =========================
@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"].strip()
    email = request.form["email"].strip()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM users WHERE name=%s",
        (name,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "User already exists."
        })

    cursor.execute(
        """
        INSERT INTO users(name,email)
        VALUES(%s,%s)
        """,
        (name, email)
    )

    conn.commit()

    user_id = cursor.lastrowid

    dataset_path = os.path.join(
        "dataset",
        str(user_id)
    )

    os.makedirs(
        dataset_path,
        exist_ok=True
    )

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "user_id": user_id,
        "message": "User created successfully."
    })


# =========================
# Train Model
# =========================
@app.route("/train")
def train():

    os.system("python3 train_model.py")

    return redirect("/")


# =========================
# Delete User
# =========================
@app.route("/delete", methods=["POST"])
def delete_user():

    username = request.form.get("username")

    if username:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE name=%s",
            (username,)
        )

        user = cursor.fetchone()

        if user:

            user_id = user["id"]

            dataset_path = os.path.join(
                "dataset",
                str(user_id)
            )

            if os.path.exists(dataset_path):
                import shutil
                shutil.rmtree(dataset_path)

            cursor.execute(
                "DELETE FROM users WHERE id=%s",
                (user_id,)
            )

            conn.commit()

        cursor.close()
        conn.close()

    return redirect("/")


# =========================
# Upload Images
# =========================
@app.route("/upload-image", methods=["POST"])
def upload_image():

    data = request.get_json()

    user_id = data.get("user_id")
    image_number = data.get("image_number")
    image_data = data.get("image")

    if not user_id or image_data is None:

        return jsonify({
            "success": False,
            "message": "Missing data."
        }), 400

    try:

        image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(
            image_data
        )

        image = Image.open(
            BytesIO(image_bytes)
        )

        dataset_path = os.path.join(
            "dataset",
            str(user_id)
        )

        os.makedirs(
            dataset_path,
            exist_ok=True
        )

        image_path = os.path.join(
            dataset_path,
            f"{image_number}.jpg"
        )

        image.save(image_path)

        return jsonify({
            "success": True,
            "message": "Image saved successfully."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================
# Browser Recognition
# =========================
@app.route("/recognize-frame", methods=["POST"])
def recognize_browser_frame():

    try:

        data = request.get_json()

        image_data = data.get("image")

        if not image_data:

            return jsonify({
                "success": False,
                "message": "No image received."
            })

        image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(
            image_data
        )

        image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        frame = np.array(image)

        result = recognize_frame(frame)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)