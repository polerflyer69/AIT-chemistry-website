from flask import Flask, render_template, request, redirect, url_for, flash, g, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-this-in-prod'
DATABASE = 'database.db'

# Auto-initialize DB if missing (Fix for Render Deployment)
if not os.path.exists(DATABASE):
    from init_db import init_db
    print("Database not found. Initializing...", flush=True)
    init_db()
else:
    print("Database found. Skipping initialization.", flush=True)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Routes ---

@app.route('/')
def home():
    conn = get_db()
    testimonials = conn.execute('SELECT * FROM testimonials WHERE is_featured = 1').fetchall()
    return render_template('home.html', testimonials=testimonials, page_class='home-page')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    student_results = None
    student_info = None
    error = None

    conn = get_db()

    # Check if student is logged in via session
    if 'student_id' in session:
        student_id = session['student_id']
        student_info = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
        if student_info:
            student_results = conn.execute(
                'SELECT * FROM test_results WHERE student_id = ? ORDER BY test_date DESC',
                (student_id,)
            ).fetchall()
    
    # Validation for manual search (keeping it optionally or for fail-safe)
    elif request.method == 'POST':
        identifier = request.form['identifier'] # Roll No or Phone
        
        # Try finding student by roll_no, parent_phone, or name
        student = conn.execute(
            'SELECT * FROM students WHERE roll_no = ? OR parent_phone = ? OR full_name LIKE ?', 
            (identifier, identifier, '%' + identifier + '%')
        ).fetchone()

        if student:
            student_info = student
            student_results = conn.execute(
                'SELECT * FROM test_results WHERE student_id = ? ORDER BY test_date DESC',
                (student['id'],)
            ).fetchall()
        else:
            error = "Student not found. Please check your Roll No or Registered Phone."

    return render_template('results.html', results=student_results, student=student_info, error=error)

@app.route('/notes')
def notes():
    if 'user' not in session and 'student_id' not in session:
        return render_template('notes.html', access_denied=True)

    conn = get_db()
    notes_by_class = {}
    visible_categories = []

    # Admin Access: See All
    if 'user' in session:
        visible_categories = ['Class 9', 'Class 10', 'Class 11', 'Class 12', 'JEE', 'NEET']
        for cat in visible_categories:
            notes_by_class[cat] = []
        all_notes = conn.execute('SELECT * FROM notes ORDER BY uploaded_at DESC').fetchall()
        for note in all_notes:
            if note['class_category'] in notes_by_class:
                notes_by_class[note['class_category']].append(note)

    # Student Access: See Only Their Class
    elif 'student_id' in session:
        student = conn.execute('SELECT class_batch FROM students WHERE id = ?', (session['student_id'],)).fetchone()
        if student:
            user_class = student['class_batch']
            visible_categories = [user_class]
            notes_by_class[user_class] = []
            
            # Fetch only meaningful notes for them (exact match or related like JEE/NEET for 11/12)
            target_classes = [user_class]
            if user_class in ['Class 11', 'Class 12']:
                target_classes.extend(['JEE', 'NEET'])
                visible_categories.extend(['JEE', 'NEET'])
                notes_by_class['JEE'] = []
                notes_by_class['NEET'] = []

            placeholders = ','.join('?' * len(target_classes))
            query = f"SELECT * FROM notes WHERE class_category IN ({placeholders}) ORDER BY uploaded_at DESC"
            student_notes = conn.execute(query, target_classes).fetchall()
            
            for note in student_notes:
                if note['class_category'] in notes_by_class:
                    notes_by_class[note['class_category']].append(note)

    return render_template('notes.html', notes=notes_by_class, visible_categories=visible_categories)


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('images', 'logo.png')


@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    name = request.form['name']
    phone = request.form['phone']
    class_type = request.form['class_type']
    message = request.form['message']

    if not name or not phone:
        flash('Name and Phone are required!')
        return redirect(url_for('contact'))

    conn = get_db()
    conn.execute(
        'INSERT INTO enquiries (student_name, class_type, phone, message) VALUES (?, ?, ?, ?)',
        (name, class_type, phone, message)
    )
    conn.commit()
    flash('Thank you! We will contact you soon.')
    return redirect(url_for('contact')) # Or home

@app.route('/submit-review', methods=['POST'])
def submit_review():
    name = request.form['student_name']
    class_info = request.form['class_info']
    rating = request.form['rating']
    content = request.form['content']

    conn = get_db()
    conn.execute(
        'INSERT INTO testimonials (student_name, class_info, rating, content, is_featured) VALUES (?, ?, ?, ?, ?)',
        (name, class_info, rating, content, 0) # 0 = Pending Approval
    )
    conn.commit()
    flash('Thank you! Your review has been submitted for approval.')
    return redirect(url_for('home'))

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/notes'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Admin Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Check if password was submitted (Step 2 of Admin Login)
        if 'password' in request.form:
            password = request.form['password']
            conn = get_db()
            admin = conn.execute('SELECT * FROM admin WHERE username = ?', ('admin',)).fetchone()
            
            # Default password 'admin' if DB has dummy hash, otherwise check real match
            stored_pass = admin['password_hash']
            # Allow 'admin' if it matches OR if it's the specific dummy seed
            is_valid = (password == stored_pass) or (password == 'admin' and 'need_impl_later' in stored_pass)
            
            if is_valid:
                session['user'] = 'admin'
                flash('Welcome back, Sir!')
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid Admin Password'
                return render_template('login.html', error=error, admin_mode=True)

        identifier = request.form['identifier'].strip()
        
        # Admin Login Trigger (Step 1)
        if identifier == 'ashwin25':
            return render_template('login.html', admin_mode=True)
        
        # Student Login
        conn = get_db()
        student = conn.execute('SELECT * FROM students WHERE roll_no = ?', (identifier,)).fetchone()
        
        if student:
            session['student_id'] = student['id']
            session['student_name'] = student['full_name']
            flash(f"Welcome, {student['full_name']}!")
            return redirect(url_for('results'))
        else:
            error = 'Invalid Code or Roll Number'
            
    return render_template('login.html', error=error)

@app.route('/admin/change_password', methods=['POST'])
def change_password():
    if 'user' not in session: return redirect(url_for('login'))
    
    new_pass = request.form['new_password']
    conn = get_db()
    conn.execute('UPDATE admin SET password_hash = ? WHERE username = ?', (new_pass, 'admin'))
    conn.commit()
    flash('Admin password updated successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    conn = get_db()
    enquiries = conn.execute('SELECT * FROM enquiries ORDER BY created_at DESC').fetchall()
    notes = conn.execute('SELECT * FROM notes ORDER BY uploaded_at DESC').fetchall()
    conn = get_db()
    enquiries = conn.execute('SELECT * FROM enquiries ORDER BY created_at DESC').fetchall()
    notes = conn.execute('SELECT * FROM notes ORDER BY uploaded_at DESC').fetchall()
    students = conn.execute('SELECT * FROM students ORDER BY full_name ASC').fetchall()
    pending_reviews = conn.execute('SELECT * FROM testimonials WHERE is_featured = 0').fetchall()
    
    return render_template('admin.html', 
                           enquiries=enquiries, 
                           notes=notes, 
                           students=students, 
                           reviews=pending_reviews)

@app.route('/admin/approve_review/<int:id>', methods=['POST'])
def approve_review(id):
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db()
    conn.execute('UPDATE testimonials SET is_featured = 1 WHERE id = ?', (id,))
    conn.commit()
    flash('Review Approved!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_review/<int:id>', methods=['POST'])
def delete_review(id):
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM testimonials WHERE id = ?', (id,))
    conn.commit()
    flash('Review Deleted.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_student', methods=['POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    try:
        conn.execute('INSERT INTO students (full_name, roll_no, parent_phone, class_batch, board) VALUES (?, ?, ?, ?, ?)',
                     (request.form['full_name'], request.form['roll_no'], request.form['parent_phone'], request.form['class_batch'], request.form.get('board')))
        conn.commit()
        flash('Student added successfully!')
    except sqlite3.IntegrityError:
        flash('Error: Roll No already exists!')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_result', methods=['POST'])
def add_result():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    conn.execute('INSERT INTO test_results (student_id, test_name, marks_obtained, total_marks, test_date) VALUES (?, ?, ?, ?, ?)',
                 (request.form['student_id'], request.form['test_name'], request.form['marks_obtained'], request.form['total_marks'], request.form['test_date']))
    conn.commit()
    flash('Result added successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/upload_note', methods=['POST'])
def upload_note():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('admin_dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin_dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique filename to prevent overwrite issues
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        title = request.form['title']
        class_category = request.form['class_category']
        board = request.form.get('board', '')
        
        conn = get_db()
        conn.execute('INSERT INTO notes (title, class_category, board, file_path) VALUES (?, ?, ?, ?)',
                     (title, class_category, board, unique_filename))
        conn.commit()
        flash('Note uploaded successfully!')
    else:
        flash('Invalid file type. PDF only.')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    # Get file path to delete file from disk too
    note = conn.execute('SELECT file_path FROM notes WHERE id = ?', (note_id,)).fetchone()
    if note:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], note['file_path']))
        except OSError:
            pass # File might not exist
            
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        flash('Note deleted.')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_enquiry/<int:id>', methods=['POST'])
def delete_enquiry(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    conn.execute('DELETE FROM enquiries WHERE id = ?', (id,))
    conn.commit()
    flash('Enquiry deleted successfully!')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    # Delete associated results first
    conn.execute('DELETE FROM test_results WHERE student_id = ?', (id,))
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    flash('Student account deleted.')
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
