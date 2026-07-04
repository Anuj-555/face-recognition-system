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
from database.db import get_connection

# Take user name from terminal
name = input("Enter Name: ")
email = input("Enter Email: ")

# Connect to database
conn = get_connection()
cursor = conn.cursor()

# Insert user into database
query = "INSERT INTO users (name, email) VALUES (%s, %s)"
cursor.execute(query, (name, email))
conn.commit()

# Get generated user id
user_id = cursor.lastrowid

# Create folder for user images
dataset_path = f"dataset/{user_id}"
os.makedirs(dataset_path, exist_ok=True)

# ---- STEP 4 FIX IS HERE ----
# Use macOS camera backend
cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not cam.isOpened():
    print("Camera could not be opened")
    exit()

print("Capturing images...")

count = 0

while True:

    ret, frame = cam.read()

    # STEP 3 FIX (prevent crash)
    if not ret:
        print("Camera not detected")
        break

    cv2.imshow("Register Face", frame)

    key = cv2.waitKey(1)

    # Press C to capture image
    if key == ord('c'):
        img_path = f"{dataset_path}/{count}.jpg"
        cv2.imwrite(img_path, frame)
        print("Saved:", img_path)
        count += 1

    # Stop after 10 images
    if count >= 10:
        break

cam.release()
cv2.destroyAllWindows()

print("User registered successfully")
