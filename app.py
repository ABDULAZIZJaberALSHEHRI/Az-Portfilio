import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Change this for your OCI production
DB_PATH = 'database.db'

UPLOAD_FOLDER = 'static/assets/certificates' # Path for certificates
PROJECT_FOLDER = 'static/assets' # Path for projects
ALLOWED_EXTENSIONS = {'pdf','png', 'jpg', 'jpeg', 'gif'} # Security whitelist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database tables if they don't exist."""
    with get_db_connection() as conn:
        # Projects Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                image_data BLOB,
                image_mimetype TEXT,
                github TEXT,
                demo TEXT
            )
        ''')
        # Certificates Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                image BLOB,
		        image_mimetype TEXT
            )
        ''')
	# skills
        conn.execute('''
            CREATE TABLE IF NOT EXISTS skills(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS icons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                image_data BLOB,
                image_mimetype TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,              -- 'Abdulaziz Alshehri'
                bio TEXT,               -- Your intro text
                career_objective TEXT,  -- Career objective statement
                image_data BLOB,        -- Your profile picture binary
                image_mimetype TEXT     -- 'image/jpeg' or 'image/png'
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,        -- e.g., 'resume'
                file_data BLOB,         -- The PDF binary
                mimetype TEXT           -- 'application/pdf'
            )
        ''')
        
        # Add career_objective column to profile table if it doesn't exist
        try:
            conn.execute('ALTER TABLE profile ADD COLUMN career_objective TEXT')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        conn.commit()

init_db()

# --- ROUTES ---
@app.route('/media/<category>/<identifier>')
def serve_media(category, identifier):
    conn = get_db_connection()
    item = None
    if category == 'icon':
        item = conn.execute('SELECT image_data, image_mimetype FROM icons WHERE name = ?', (identifier,)).fetchone()
    elif category == 'project':
        item = conn.execute('SELECT image_data, image_mimetype FROM projects WHERE id = ?', (identifier,)).fetchone()
    elif category == 'certificate':
        # FIXED: Changed 'image_data' to 'image' to match your 'certificates' table schema
        item = conn.execute('SELECT image as image_data, image_mimetype FROM certificates WHERE id = ?', (identifier,)).fetchone()
    elif category == 'document':
        item = conn.execute('SELECT file_data as image_data, mimetype as image_mimetype FROM documents WHERE name = ?', (identifier,)).fetchone()
    conn.close()
    
    if item and item['image_data']:
        return Response(item['image_data'], mimetype=item['image_mimetype'])
    return "", 404

@app.route('/')
def index():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    certificates = conn.execute('SELECT * FROM certificates LIMIT 2').fetchall()
    skills = conn.execute('SELECT * FROM skills').fetchall()
    profile = conn.execute('SELECT * FROM profile WHERE id = 1').fetchone()
    conn.close()
    return render_template('index.html', projects=projects, certificates=certificates, skills=skills, profile=profile, admin=session.get('logged_in'))

@app.route('/edit/skill/<int:id>', methods=['GET', 'POST'])
def edit_skill(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('UPDATE skills SET name=?, level=?, category=? WHERE id=?', (request.form['name'], request.form['level'], request.form['category'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    skill = conn.execute('SELECT * FROM skills WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_skill.html', skill=skill)

@app.route('/certificates')
def all_certificates():
    conn = get_db_connection()
    certificates = conn.execute('SELECT * FROM certificates').fetchall()
    conn.close()
    return render_template('certificates.html', 
                           certificates=certificates, 
                           admin=session.get('logged_in'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 'password' here refers to the name attribute in your HTML: <input name="password">
        user_input = request.form.get('password') 
        
        # Compare it against the password stored in your .env file
        if user_input == os.getenv('ADMIN_PASSWORD'): 
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid Password')
            
    return render_template('login.html')

@app.route('/logout')   
def logout():   
    session.pop('logged_in', None)  
    return redirect(url_for('index'))   

@app.route('/edit/<type>/<int:id>', methods=['GET', 'POST'])
def edit_item(type, id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    table = 'projects' if type == 'project' else 'certificates'
    # Use 'image' for certificates to match your schema
    img_col = 'image_data' if type == 'project' else 'image'
    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        file = request.files.get('image_file')
        
        if file and file.filename != '':
            binary_data = file.read()
            mimetype = file.mimetype
            conn.execute(f'UPDATE {table} SET title=?, {img_col}=?, image_mimetype=? WHERE id=?', 
                         (title, binary_data, mimetype, id))
        else:
            conn.execute(f'UPDATE {table} SET title=? WHERE id=?', (title, id))
            
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    item = conn.execute(f'SELECT * FROM {table} WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_item.html', item=item, type=type)


@app.route('/add/<type>', methods=['GET', 'POST'])
def add_item(type):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        file = request.files.get('image_file') 
        
        if file:
            binary_data = file.read() 
            mimetype = file.mimetype 
            
            conn = get_db_connection()
            if type == 'project':
                conn.execute('''
                    INSERT INTO projects (title, image_data, image_mimetype, github, demo)
                    VALUES (?, ?, ?, ?, ?)''', 
                    (title, binary_data, mimetype, request.form['github'], request.form['demo']))
            else:
                # FIXED: Changed 'title_data' to 'image' to match your certificates table
                conn.execute('''
                    INSERT INTO certificates (title, image, image_mimetype)
                    VALUES (?, ?, ?)''', 
                    (title, binary_data, mimetype))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
            
    return render_template('add_item.html', type=type)

@app.route('/profile_image')
def get_profile_image():
    conn = get_db_connection()
    # We always fetch ID 1 since there is only one profile
    user = conn.execute('SELECT image_data, image_mimetype FROM profile WHERE id = 1').fetchone()
    conn.close()
    if user and user['image_data']:
        return Response(user['image_data'], mimetype=user['image_mimetype'])
    return "" # Or a default avatar

@app.route('/edit/profile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        career_objective = request.form.get('career_objective')
        file = request.files.get('image_file')
        
        if file and file.filename != '':
            binary_data = file.read()
            mimetype = file.mimetype
            conn.execute('UPDATE profile SET name=?, bio=?, career_objective=?, image_data=?, image_mimetype=? WHERE id=1',
                         (name, bio, career_objective, binary_data, mimetype))
        else:
            conn.execute('UPDATE profile SET name=?, bio=?, career_objective=? WHERE id=1',
                         (name, bio, career_objective))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    profile = conn.execute('SELECT * FROM profile WHERE id = 1').fetchone()
    conn.close()
    return render_template('edit_profile.html', profile=profile)

@app.route('/edit/cv', methods=['GET', 'POST'])
def edit_cv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        file = request.files.get('cv_file')
        
        if file and file.filename != '':
            binary_data = file.read()
            mimetype = file.mimetype
            
            # Check if resume already exists
            existing = conn.execute('SELECT id FROM documents WHERE name = ?', ('resume',)).fetchone()
            
            if existing:
                conn.execute('UPDATE documents SET file_data=?, mimetype=? WHERE name=?',
                             (binary_data, mimetype, 'resume'))
            else:
                conn.execute('INSERT INTO documents (name, file_data, mimetype) VALUES (?, ?, ?)',
                             ('resume', binary_data, mimetype))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            conn.close()
            return redirect(url_for('edit_cv'))
    
    cv = conn.execute('SELECT * FROM documents WHERE name = ?', ('resume',)).fetchone()
    conn.close()
    return render_template('edit_cv.html', cv=cv)

# --- ADD SKILL ROUTE ---
@app.route('/add/skill', methods=['GET', 'POST'])
def add_skill():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        category = request.form['category']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO skills (name, level, category) VALUES (?, ?, ?)',
                     (name, level, category))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_skill.html')

# --- DELETE SKILL ROUTE ---
@app.route('/delete/skill/<int:id>')
def delete_skill(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM skills WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# --- DELETE CERTIFICATE ROUTE ---
@app.route('/delete/certificate/<int:id>')
def delete_certificate(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM certificates WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('all_certificates'))

# --- DELETE PROJECT ROUTE ---
@app.route('/delete/project/<int:id>')
def delete_project(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Get port from environment variable or default to 5000 for local development
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

