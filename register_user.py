# import cv2
# import os
# from database.db import get_connection

# name = input("Enter Name: ")
# email = input("Enter Email: ")

# # Save user in database
# conn = get_connection()
# cursor = conn.cursor()

# query = "INSERT INTO users (name,email) VALUES (%s,%s)"
# cursor.execute(query,(name,email))
# conn.commit()

# cursor.close()
# conn.close()

# # Create user dataset folder
# path = f"dataset/{name}"

# if not os.path.exists(path):
#     os.makedirs(path)

# cap = cv2.VideoCapture(0)

# count = 0

# print("Capturing images...")

# while True:

#     ret, frame = cap.read()
    

#     cv2.imshow("Register Face", frame)

#     file_path = f"{path}/{count}.jpg"
#     cv2.imwrite(file_path, frame)

#     count += 1

#     if count == 20:
#         break

#     if cv2.waitKey(1) == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

# print("User registered successfully.")



import cv2
import os
import sys
from database.db import get_connection

# Check command-line arguments
if len(sys.argv) < 3:
    print("Usage: python register_user.py <name> <email>")
    sys.exit()

name = sys.argv[1].strip()
email = sys.argv[2].strip()

# Connect to database
conn = get_connection()
cursor = conn.cursor()

# Check if user already exists
cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
existing_user = cursor.fetchone()

if existing_user:
    print(f"User '{name}' already exists.")
    cursor.close()
    conn.close()
    sys.exit()

# Insert user into database
query = "INSERT INTO users (name, email) VALUES (%s, %s)"
cursor.execute(query, (name, email))
conn.commit()

# Get generated user id
user_id = cursor.lastrowid

# Close database connection
cursor.close()
conn.close()

# Create folder using user id
dataset_path = os.path.join("dataset", str(user_id))
os.makedirs(dataset_path, exist_ok=True)

# Open camera (macOS)
cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not cam.isOpened():
    print("Camera could not be opened")
    sys.exit()

print("Capturing images...")
print("Press 'C' to capture each image.")

count = 0

while True:

    ret, frame = cam.read()

    if not ret:
        print("Camera not detected")
        break

    cv2.imshow("Register Face", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):
        img_path = os.path.join(dataset_path, f"{count}.jpg")
        cv2.imwrite(img_path, frame)
        print(f"Saved: {img_path}")
        count += 1

    # Stop after 10 images
    if count >= 10:
        break

    # ESC to cancel
    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()

print("User registered successfully.")
