
import sqlite3
import os


# Database file location
DATABASE_PATH = "database/hr_assistant.db"


def get_connection():

    # Create database folder if it doesn't exist
    os.makedirs("database", exist_ok=True)

    # Connect to SQLite database
    connection = sqlite3.connect(DATABASE_PATH)

    # Return connection
    return connection


if __name__ == "__main__":

    connection = get_connection()

    print("Database connected successfully!")

    connection.close()
