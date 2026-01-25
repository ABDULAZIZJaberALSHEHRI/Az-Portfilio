import sqlite3

def seed_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Clear existing data to avoid duplicates if you run this twice
    cursor.execute('DELETE FROM projects')
    cursor.execute('DELETE FROM certificates')

    # 2. Your Projects (from index.html)
    projects = [
        ('Namaa website', './assets/namaa logo.jpg', 'https://github.com/ABDULAZIZJaberALSHEHRI/namaa-final-project.git', 'https://www.figma.com/proto/GrigRVExBXpmD2yZGxl4rW/Namaa-platform?node-id=1-3370...'),
        ('Mudaris website', './assets/Mudaris logo.png', 'https://github.com/ABDULAZIZJaberALSHEHRI/Capstone-2.git', 'https://www.figma.com/proto/dU7JVLelisUK5msgxHhaW7/Exerice-figma?node-id=4-121...'),
        ('Bank system simulator', './assets/bank account.jpg', 'https://github.com/ABDULAZIZJaberALSHEHRI/project3.git', None),
        ('Captain Naqel website', './assets/Captain Naqel_transparent-.png', 'https://github.com/ABDULAZIZJaberALSHEHRI/Capstone-3.git', None)
    ]

    cursor.executemany('''
        INSERT INTO projects (title, image, github, demo) 
        VALUES (?, ?, ?, ?)
    ''', projects)

    # 3. Your Certificates (from certificates.html)
    certificates = [
        ('Full Stack Java Developer', './assets/certificates/Full Stack Java Developer.png'),
        ('Object-Oriented Programming', './assets/certificates/oop.png'),
        ('BootStrap', './assets/certificates/BootStrap102.png'),
        ('Css', './assets/certificates/Css.png'),
        ('Dom', './assets/certificates/DOM.png'),
        ('Git 101', './assets/certificates/Git 101.png'),
        ('HTML', './assets/certificates/HTML.png'),
        ('JavaScript 101', './assets/certificates/JS 101.png'),
        ('JavaScript 102', './assets/certificates/JS 102.png'),
        ('SQL 101', './assets/certificates/SQL 101.png')
    ]

    cursor.executemany('''
        INSERT INTO certificates (title, image) 
        VALUES (?, ?)
    ''', certificates)

    conn.commit()
    conn.close()
    print("Database seeded with your existing projects and certificates!")

if __name__ == "__main__":
    seed_database()
