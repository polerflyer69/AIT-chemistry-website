import sqlite3
import os

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        
    conn = get_db_connection()
    
    # Use absolute path to find schema.sql regardless of CWD
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    with open(schema_path) as f:
        conn.executescript(f.read())
    
    # Create default admin
    conn.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)",
                 ('admin', 'scrypt:32768:8:1$need_impl_later$hash'))
    
    # Seed Chemistry-focused Testimonials (Parent & Student mix for trust)
    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Rohan's Parent", "We saw a significant improvement in his Chemistry scores. Sir's personal attention made all the difference.", "Class 12 - Parent", 5, 1))
    
    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Priya Mehta", "Organic Chemistry was customized to be very easy to understand. The notes are excellent for Boards.", "Class 12 - Board", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Arjun Patel", "The best place for JEE Chemistry in Vadodara. Detailed concept clarity.", "JEE Aspirant", 5, 1))

    # New Reviews from Screenshots
    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Khushi Bhavsar", "Material was clearly explained, making complex concepts easier to understand. Appreciated the balance between lectures and real-world applications. Highly recommend!", "Chemistry Student", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Nitya Agrawal", "Best chemistry classes I've ever come across. Ashwin sir engages well and keeps our interest intact. Weekly tests help us recognize and correct mistakes.", "Chemistry Student", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Divyanshi Gohil", "Ashwin sir's teaching style is easy going. He creates a comfortable environment where students understand concepts rather than mugging up. Hands down the best in his field.", "Parent", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Cyril Shiju", "Engaging and informative classes. Well-structured lessons made complex topics easier to understand with clear explanations.", "Chemistry Student", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Hetvi Sukhadiya", "Teacher explains everything clearly. The environment is friendly and comfortable. Highly recommended!", "Chemistry Student", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Diva Kapadia", "Ashwin sir is an excellent educator. His teaching style is engaging and makes learning enjoyable. His dedication is incredible.", "Chemistry Student", 5, 1))

    conn.execute("INSERT INTO testimonials (student_name, content, class_info, rating, is_featured) VALUES (?, ?, ?, ?, ?)",
                 ("Krisha Upadhyay", "Great teacher with deep subject knowledge. Always ready to solve doubts and gives personal attention. Helps build confidence.", "Chemistry Student", 5, 1))

    # Seed Student
    conn.execute("INSERT INTO students (full_name, roll_no, parent_phone, class_batch) VALUES (?, ?, ?, ?)",
                 ("Rohan Sharma", "AIT001", "9876543210", "Class 12"))
                 
    # Seed Chemistry Result
    conn.execute("INSERT INTO test_results (student_id, test_name, marks_obtained, total_marks, test_date) VALUES (?, ?, ?, ?, ?)",
                 (1, "Solid State & Solutions", 45, 50, "2025-12-15"))

    conn.commit()
    conn.close()
    print("Database initialized with Chemistry data.")

if __name__ == '__main__':
    init_db()
