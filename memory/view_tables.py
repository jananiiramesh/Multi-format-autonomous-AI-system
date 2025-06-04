import sqlite3

def view_all_tables(db_path="shared_memory.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        print(f"\n=== Contents of table: {table_name} ===")
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        col_names = [description[0] for description in cursor.description]
        print(" | ".join(col_names))
        print("-" * 40)
        
        for row in rows:
            print(" | ".join(str(item) for item in row))
    
    conn.close()

if __name__ == "__main__":
    view_all_tables()
