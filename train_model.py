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



import face_recognition
import os
import pickle

dataset_path = "dataset"
model_path = "models/encodings.pickle"

known_encodings = []
known_names = []

print("Training model...")

# Loop through each user folder
for user in os.listdir(dataset_path):

    user_path = os.path.join(dataset_path, user)

    # ✅ Skip hidden files like .DS_Store
    if not os.path.isdir(user_path):
        continue

    # Loop through each image inside user folder
    for image_name in os.listdir(user_path):

        image_path = os.path.join(user_path, image_name)

        # ✅ Skip hidden/system files
        if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                known_encodings.append(encodings[0])
                known_names.append(user)

        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue

# Save encodings
data = {
    "encodings": known_encodings,
    "names": known_names
}

os.makedirs("models", exist_ok=True)

with open(model_path, "wb") as f:
    pickle.dump(data, f)

print("Model trained successfully.")
print(f"Total faces encoded: {len(known_encodings)}")