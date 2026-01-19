import sqlite3

DATABASE = 'database.db'

def migrate():
    conn = sqlite3.connect(DATABASE)
    try:
        print("Attempting to add 'board' column to 'students' table...")
        conn.execute('ALTER TABLE students ADD COLUMN board TEXT')
        conn.commit()
        print("Migration successful: 'board' column added.")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("Migration skipped: 'board' column already exists.")
        else:
            print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
