import sqlite3

DB_PATH = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create videos table with created_at column
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT,
            description TEXT,
            upload_date TEXT,
            user_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Add views column if it doesn't exist
    try:
        c.execute("ALTER TABLE videos ADD COLUMN views INTEGER DEFAULT 0")
        print("✅ 'views' column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ 'views' column already exists.")
        else:
            print(f"⚠️ Warning: {e}")
    
    conn.commit()
    conn.close()
    print('✅ Database initialized.')

if __name__ == '__main__':
    init_db()
