import sqlite3

conn = sqlite3.connect('portfolio.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE skills ADD COLUMN icon BLOB;')
    conn.commit()
    print("Success: 'icon' column added to 'skills' table.")
except sqlite3.OperationalError:
    print("Notice: 'icon' column might already exist.")
finally:
    conn.close()
