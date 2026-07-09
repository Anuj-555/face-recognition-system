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



import os
import sys

from database.db import get_connection


# ===========================
# Check Arguments
# ===========================
if len(sys.argv) < 3:
    print("Usage: python register_user.py <name> <email>")
    sys.exit()


name = sys.argv[1].strip()
email = sys.argv[2].strip()


# ===========================
# Database Connection
# ===========================
conn = get_connection()
cursor = conn.cursor()


# ===========================
# Check Existing User
# ===========================
cursor.execute(
    "SELECT id FROM users WHERE name=%s",
    (name,)
)

existing_user = cursor.fetchone()

if existing_user:

    print("User already exists.")

    cursor.close()
    conn.close()

    sys.exit()


# ===========================
# Insert User
# ===========================
cursor.execute(
    """
    INSERT INTO users(name,email)
    VALUES(%s,%s)
    """,
    (name, email)
)

conn.commit()

user_id = cursor.lastrowid


# ===========================
# Create Dataset Folder
# ===========================
dataset_path = os.path.join(
    "dataset",
    str(user_id)
)

os.makedirs(dataset_path, exist_ok=True)


# ===========================
# Close Connection
# ===========================
cursor.close()
conn.close()


# ===========================
# Output
# ===========================
print("===================================")
print("User Registered Successfully")
print(f"User ID : {user_id}")
print(f"Dataset : {dataset_path}")
print("===================================")