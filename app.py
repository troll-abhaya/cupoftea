from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for sessions

UPLOAD_FOLDER = 'static/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, filename TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['video']

        if file and file.filename:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO videos (title, filename) VALUES (?, ?)", (title, filename))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/watch/<int:video_id>')
def watch(video_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE id=?", (video_id,))
    video = c.fetchone()
    conn.close()
    return render_template('watch.html', video=video)

# Simple fake login system for demo
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        # You can add password validation here
        if username:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Please enter a username")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', username=session['username'])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
