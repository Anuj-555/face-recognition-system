import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="anujmysql",
        database="face_recognition"
    )
    return connection