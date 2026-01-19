DROP TABLE IF EXISTS enquiries;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS test_results;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS testimonials;
DROP TABLE IF EXISTS admin;

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE enquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    class_type TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'New' -- New, Contacted, Enrolled
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    parent_phone TEXT NOT NULL,
    class_batch TEXT NOT NULL, -- Class 11, Class 12, JEE
    board TEXT, -- CBSE, GSEB, etc.
    joined_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    marks_obtained REAL NOT NULL,
    total_marks REAL NOT NULL,
    test_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL, -- Chapter / Topic Name
    class_category TEXT NOT NULL, -- Class 9, 10, 11, 12, JEE
    board TEXT, -- CBSE, ICSE, etc.
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE testimonials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    content TEXT NOT NULL,
    class_info TEXT NOT NULL,
    rating INTEGER DEFAULT 5,
    is_featured INTEGER DEFAULT 0
);
