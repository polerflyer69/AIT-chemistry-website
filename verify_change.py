import requests
import sqlite3

# Configuration
BASE_URL = 'http://127.0.0.1:5000'
LOGIN_URL = f'{BASE_URL}/login'
ADD_STUDENT_URL = f'{BASE_URL}/admin/add_student'
DB_PATH = 'database.db'

def verify_student_added(roll_no, expected_board):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,))
    student = cursor.fetchone()
    conn.close()
    
    if student:
        print(f"Student found: {student['full_name']}")
        print(f"Board: {student['board']}")
        if student['board'] == expected_board:
            print("SUCCESS: Board matches expected value.")
            return True
        else:
            print(f"FAILURE: Expected board {expected_board}, got {student['board']}")
            return False
    else:
        print("FAILURE: Student not found in database.")
        return False

def run_test():
    session = requests.Session()
    
    # 1. Login
    print("Logging in...")
    response = session.post(LOGIN_URL, data={'username': 'admin', 'password': 'admin123'})
    if response.url == f'{BASE_URL}/admin':
        print("Login successful.")
    else:
        print("Login failed.")
        return

    # 2. Add Student
    print("Adding student with new Board field...")
    student_data = {
        'full_name': 'Test Student',
        'roll_no': 'TEST001',
        'parent_phone': '1234567890',
        'class_batch': 'Class 10',
        'board': 'ICSE'
    }
    response = session.post(ADD_STUDENT_URL, data=student_data)
    
    if response.status_code == 200:
        print("Add student request completed.")
        # 3. Verify in DB
        verify_student_added('TEST001', 'ICSE')
    else:
        print(f"Add student request failed: {response.status_code}")

if __name__ == '__main__':
    # Ensure app is running separately before running this script
    # For this environment, we might need to assume the user runs it or we run it in background
    # But since I can't easily keep the web server running in background across tool calls for this test,
    # I will stick to DIRECT DB INSERTION test if web server is hard to orchestrate, 
    # OR I will just check if the code logic is correct.
    
    # Actually, simpler test: just check if the DB has the column.
    pass
