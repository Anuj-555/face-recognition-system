from flask import Flask, render_template, redirect, request
import os
import sys
import json
from datetime import date

from database.db import get_connection

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

    # Total registered users
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()["total_users"]

    # Total attendance records
    cursor.execute("SELECT COUNT(*) AS total_attendance FROM attendance")
    total_attendance = cursor.fetchone()["total_attendance"]

    # Today's attendance
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

    # AI Model Status
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

    name = request.form["name"]
    email = request.form["email"]

    os.system(f'{sys.executable} register_user.py "{name}" "{email}"')

    return redirect("/")


# =========================
# Train Model
# =========================
@app.route("/train")
def train():

    os.system(f"{sys.executable} train_model.py")

    return redirect("/")


# =========================
# Start Recognition
# =========================
@app.route("/recognize")
def recognize():

    os.system(f"{sys.executable} recognize.py")

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

        # Find user id
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


if __name__ == "__main__":
    app.run(debug=True)