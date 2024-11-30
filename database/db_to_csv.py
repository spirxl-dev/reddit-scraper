import sqlite3
import csv

def export_table_to_csv(db_path, table_name, output_csv_path):
    """
    Export the contents of a SQLite table to a CSV file.

    Args:
        db_path (str): Path to the SQLite database.
        table_name (str): Name of the table to export.
        output_csv_path (str): Path to the output CSV file.
    """
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow(column_names)
            writer.writerows(rows)

        print(f"Table '{table_name}' exported successfully to '{output_csv_path}'.")
    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
    finally:
        if connection:
            connection.close()

# Example usage
if __name__ == "__main__":
    db_path = "database/data.db" 
    table_name = "posts"
    output_csv_path = "posts.csv" 

    export_table_to_csv(db_path, table_name, output_csv_path)