# import face_recognition
# import os
# import pickle

# dataset_path = "dataset"

# known_encodings = []
# known_names = []

# print("Training model...")

# for user in os.listdir(dataset_path):

#     user_path = os.path.join(dataset_path, user)

#     for image_name in os.listdir(user_path):

#         image_path = os.path.join(user_path, image_name)

#         image = face_recognition.load_image_file(image_path)

#         encodings = face_recognition.face_encodings(image)

#         if len(encodings) > 0:
#             known_encodings.append(encodings[0])
#             known_names.append(user)

# data = {
#     "encodings": known_encodings,
#     "names": known_names
# }

# with open("models/encodings.pickle","wb") as f:
#     pickle.dump(data,f)

# print("Model trained successfully.")



import os
import pickle
import face_recognition

from database.db import get_connection

dataset_path = "dataset"
model_path = "models/encodings.pickle"

known_encodings = []
known_names = []
known_ids = []
known_emails = []

print("===================================")
print("Training model...")
print("===================================")

# Check dataset folder
if not os.path.exists(dataset_path):
    print("Dataset folder not found!")
    exit()

# Connect to MySQL
conn = get_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT id, name, email FROM users")
users = cursor.fetchall()

if len(users) == 0:
    print("No users found in database.")
    cursor.close()
    conn.close()
    exit()

for user in users:

    user_id = user["id"]
    name = user["name"]
    email = user["email"]

    print(f"\nProcessing User: {name} (ID: {user_id})")

    # Dataset folder is USER ID
    user_path = os.path.join(dataset_path, str(user_id))

    if not os.path.exists(user_path):
        print(f"❌ Folder not found: {user_path}")
        continue

    image_count = 0

    for image_name in os.listdir(user_path):

        if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(user_path, image_name)

        try:

            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) == 0:
                print(f"No face found in {image_name}")
                continue

            known_encodings.append(encodings[0])
            known_names.append(name)
            known_ids.append(user_id)
            known_emails.append(email)

            image_count += 1

        except Exception as e:
            print(f"Error processing {image_name}: {e}")

    print(f"Encoded {image_count} image(s).")

cursor.close()
conn.close()

data = {
    "encodings": known_encodings,
    "names": known_names,
    "ids": known_ids,
    "emails": known_emails
}

os.makedirs("models", exist_ok=True)

with open(model_path, "wb") as f:
    pickle.dump(data, f)

print("\n===================================")
print("Training Complete")
print(f"Total Faces Encoded : {len(known_encodings)}")
print(f"Total Users Encoded : {len(set(known_ids))}")
print("Model saved to:", model_path)
print("===================================")