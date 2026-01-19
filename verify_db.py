import sqlite3

DATABASE = 'database.db'

def check_schema():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    if 'board' in columns:
        print("SUCCESS: 'board' column exists in 'students' table.")
    else:
        print("FAILURE: 'board' column missing.")

if __name__ == '__main__':
    check_schema()
