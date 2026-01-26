import sqlite3
import os

def migrate():
    conn = sqlite3.connect('database.db')
    
    # 1. Icons
    icons = ['github.png', 'linkedin.png', 'phone icon.png', 'checkmark.png', 'arrow.png', 'email.png', 'experience.png', 'education.png']
    for icon in icons:
        path = f'static/assets/{icon}'
        if os.path.exists(path):
            with open(path, 'rb') as f:
                conn.execute('INSERT OR REPLACE INTO icons (name, image_data, image_mimetype) VALUES (?, ?, ?)',
                             (icon.split('.')[0], f.read(), 'image/png'))

    # 2. Profile & Resume (only insert if not exists)
    # Check if profile exists, if not insert initial data
    profile_exists = conn.execute('SELECT id FROM profile WHERE id = 1').fetchone()
    if not profile_exists:
        with open('static/assets/profile_pic.jpg', 'rb') as f:
            conn.execute('INSERT INTO profile (id, name, bio, image_data, image_mimetype) VALUES (1, "Abdulaziz Alshehri", "Backend Developer...", ?, "image/jpeg")', (f.read(),))
    
    # Check if resume exists, if not insert initial data
    resume_exists = conn.execute('SELECT id FROM documents WHERE name = "resume"').fetchone()
    if not resume_exists:
        with open('static/assets/Abdulaziz Alshehri, software engineering (CV).pdf', 'rb') as f:
            conn.execute('INSERT INTO documents (name, file_data, mimetype) VALUES ("resume", ?, "application/pdf")', (f.read(),))

    # 3. Skills (only insert default skills if table is empty)
    skills_exist = conn.execute('SELECT COUNT(*) FROM skills').fetchone()[0]
    
    if skills_exist == 0:
        # Only insert default skills if no skills exist
        default_skills = [('JAVA', 'Advanced', 'backend'), ('SPRINGBOOT', 'Advanced', 'backend'), ('HTML', 'Intermediate', 'frontend')]
        conn.executemany('INSERT INTO skills (name, level, category) VALUES (?, ?, ?)', default_skills)

    conn.commit()
    conn.close()
    print("Migration Success!")

if __name__ == '__main__':
    migrate()