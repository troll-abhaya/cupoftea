import sqlite3
from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
        db.row_factory = sqlite3.Row
    return db

def get_user_stats(user_id):
    db = get_db()
    # Total likes on user's videos (if likes column exists)
    try:
        likes = db.execute('SELECT SUM(likes) as total_likes FROM videos WHERE user_id = ?', (user_id,)).fetchone()['total_likes'] or 0
    except Exception:
        likes = 0
    # Followers (if followers table exists)
    try:
        followers = db.execute('SELECT COUNT(*) as total_followers FROM followers WHERE following_id = ?', (user_id,)).fetchone()['total_followers'] or 0
        following = db.execute('SELECT COUNT(*) as total_following FROM followers WHERE follower_id = ?', (user_id,)).fetchone()['total_following'] or 0
    except Exception:
        followers = 0
        following = 0
    # Total views on user's videos
    try:
        views = db.execute('SELECT SUM(views) as total_views FROM videos WHERE user_id = ?', (user_id,)).fetchone()['total_views'] or 0
    except Exception:
        views = 0
    subscribers = followers
    return {
        'likes': likes,
        'followers': followers,
        'following': following,
        'subscribers': subscribers,
        'views': views
    }
