import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# Import user_stats from the correct location
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from user_stats import get_user_stats
import subprocess
from generate_thumbnail import generate_thumbnail, generate_video_thumbnail

UPLOAD_FOLDER = 'static/videos'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB
app.secret_key = 'your_secret_key'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── DATABASE SETUP ───────────────────────────────────────────
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            description TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        db.commit()

# Add missing column if needed
def add_views_column_if_missing():
    db = get_db()
    try:
        db.execute("ALTER TABLE videos ADD COLUMN views INTEGER DEFAULT 0")
        db.commit()
        print("✅ 'views' column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ 'views' column already exists.")
        else:
            raise e

# ─── ROUTES ──────────────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    videos = db.execute("""
        SELECT v.id, v.title, v.filename, v.views, v.created_at, u.username as uploader
        FROM videos v LEFT JOIN users u ON v.user_id = u.id 
        ORDER BY v.created_at DESC
    """).fetchall()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash('You need to login to upload videos', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        file = request.files['video']

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Generate thumbnail
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            thumbnail_dir = os.path.join('static', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_path = os.path.join(thumbnail_dir, f"{os.path.splitext(filename)[0]}.jpg")
            try:
                generate_thumbnail(video_path, thumbnail_path)
                # Generate video clip thumbnail
                clip_path = os.path.join(thumbnail_dir, f"{os.path.splitext(filename)[0]}_clip.mp4")
                generate_video_thumbnail(video_path, clip_path)
            except Exception as e:
                flash(f'Video uploaded, but failed to generate thumbnail: {e}', 'error')

            db = get_db()
            db.execute(
                'INSERT INTO videos (user_id, title, filename, description, created_at) VALUES (?, ?, ?, ?, ?)',
                (session['user_id'], title, filename, description, datetime.now())
            )
            db.commit()
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('No video file selected', 'error')

    return render_template('upload.html')

@app.route('/watch/<int:video_id>')
def watch(video_id):
    db = get_db()
    db.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (video_id,))
    video = db.execute("""
        SELECT v.*, u.username as uploader 
        FROM videos v LEFT JOIN users u ON v.user_id = u.id 
        WHERE v.id = ?
    """, (video_id,)).fetchone()
    db.commit()

    if not video:
        flash('Video not found', 'error')
        return redirect(url_for('index'))

    return render_template('watch.html', video=video)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error="Please enter both username and password")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to login to view your profile', 'error')
        return redirect(url_for('login'))

    db = get_db()
    videos = db.execute("""
        SELECT v.id, v.title, v.filename, v.views, v.created_at 
        FROM videos v WHERE v.user_id = ? 
        ORDER BY v.created_at DESC
    """, (session['user_id'],)).fetchall()

    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    stats = get_user_stats(session['user_id'])

    return render_template('profile.html', username=session['username'], videos=videos, user=user, stats=stats)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            return render_template('signup.html', error="Please enter both username and password")

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        db = get_db()
        existing_user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing_user:
            return render_template('signup.html', error="Username already exists")

        hashed_password = generate_password_hash(password)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        db.commit()

        user_id = cursor.lastrowid
        session['user_id'] = user_id
        session['username'] = username
        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    db = get_db()
    videos = []
    if query:
        videos = db.execute('''
            SELECT v.id, v.title, v.filename, v.views, v.created_at, u.username as uploader
            FROM videos v LEFT JOIN users u ON v.user_id = u.id
            WHERE v.title LIKE ? OR v.filename LIKE ?
            ORDER BY v.created_at DESC
        ''', (f'%{query}%', f'%{query}%')).fetchall()
    return render_template('index.html', videos=videos, search_query=query)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/how-to-earn')
def how_to_earn():
    return render_template('how_to_earn.html')

# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    with app.app_context():
        add_views_column_if_missing()
    app.run(debug=True)
