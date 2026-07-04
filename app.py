# 

from flask import Flask, render_template, redirect, request
import os
import sys
from database.db import get_connection

app = Flask(__name__)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Register User Route
@app.route("/register", methods=["POST"])
def register():
    os.system(f"{sys.executable} register_user.py")
    return redirect("/")


# Train Model Route
@app.route("/train")
def train():
    os.system(f"{sys.executable} train_model.py")
    return redirect("/")


# Recognize Route
@app.route("/recognize")
def recognize():
    os.system(f"{sys.executable} recognize.py")
    return redirect("/")


# Delete User Route
@app.route("/delete", methods=["POST"])
def delete_user():
    username = request.form.get("username")

    if username:
        # Delete dataset folder
        dataset_path = os.path.join("dataset", username)
        if os.path.exists(dataset_path):
            import shutil
            shutil.rmtree(dataset_path)

        # Delete from database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE name=%s", (username,))
        conn.commit()
        cursor.close()
        conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)