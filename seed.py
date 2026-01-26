import sqlite3

def seed_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Your Projects (from index.html) - only insert if table is empty
    projects_exist = cursor.execute('SELECT COUNT(*) FROM projects').fetchone()[0]
    
    if projects_exist == 0:
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
        print("Projects seeded successfully!")
    else:
        print(f"Projects already exist ({projects_exist}). Skipping project insertion.")

    # 2. Your Certificates (from certificates.html) - only insert if table is empty
    certificates_exist = cursor.execute('SELECT COUNT(*) FROM certificates').fetchone()[0]
    
    if certificates_exist == 0:
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
        print("Certificates seeded successfully!")
    else:
        print(f"Certificates already exist ({certificates_exist}). Skipping certificate insertion.")

    conn.commit()
    conn.close()
    print("Database seed operation completed!")

if __name__ == "__main__":
    seed_database()
