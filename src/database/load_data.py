
import pandas as pd
from src.database.db_connection import get_connection


def load_csv_data():

    connection = get_connection()

    # CSV files and their corresponding database tables
    datasets = {
        "employees": "data/employees.csv",
        "leave_requests": "data/leave_requests.csv",
        "attendance": "data/attendance.csv",
        "holidays": "data/holidays.csv",
        "comp_off": "data/comp_off.csv"
    }

    try:
        for table_name, file_path in datasets.items():

            # Read CSV file
            df = pd.read_csv(file_path)

            # Clear old records to prevent duplicates on reruns
            connection.execute(f"DELETE FROM {table_name}")

            # Insert CSV records into SQLite
            df.to_sql(
                table_name,
                connection,
                if_exists="append",
                index=False
            )

            print(
                f"{table_name}: {len(df)} records imported successfully"
            )

        connection.commit()
        print("\nAll HR datasets imported successfully!")

    except Exception as error:
        connection.rollback()
        print("Error importing data:", error)

    finally:
        connection.close()


if __name__ == "__main__":
    load_csv_data()
