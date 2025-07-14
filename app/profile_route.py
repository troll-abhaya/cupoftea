from app.user_stats import get_user_stats
from flask import session, render_template, g, request, redirect, url_for, flash
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

def edit_profile_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        bio = request.form.get('bio')
        db.execute("UPDATE users SET username = ?, email = ?, bio = ? WHERE id = ?", (username, email, bio, session['user_id']))
        db.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile_route'))
    return render_template('edit_profile.html', user=user)
