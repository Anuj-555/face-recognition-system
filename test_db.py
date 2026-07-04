from database.db import get_connection

conn = get_connection()

if conn.is_connected():
    print("Database connected successfully")

conn.close()