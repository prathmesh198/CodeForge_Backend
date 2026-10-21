import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456789",
        database="codeforge"
    )

    return connection