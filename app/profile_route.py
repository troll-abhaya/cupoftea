from app.user_stats import get_user_stats
from flask import session, render_template, g
from app import get_db

def profile_route():
    if 'user_id' not in session:
        return render_template('login.html', error='You need to login to view your profile')
    db = get_db()
    videos = db.execute("""
        SELECT v.id, v.title, v.filename, v.views, v.created_at 
        FROM videos v WHERE v.user_id = ? 
        ORDER BY v.created_at DESC
    """, (session['user_id'],)).fetchall()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    stats = get_user_stats(session['user_id'])
    return render_template('profile.html', username=session['username'], videos=videos, user=user, stats=stats)
