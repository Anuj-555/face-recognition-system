import os
import shutil
from database.db import get_connection

user_id = input("Enter User ID to delete: ")

conn = get_connection()
cursor = conn.cursor()

# Delete user from database
cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
conn.commit()

# Delete dataset images
folder_path = f"dataset/{user_id}"

if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
    print("User images deleted")
else:
    print("No dataset folder found")

print("User deleted successfully")