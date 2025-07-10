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
    # Total likes on user's videos
    likes = db.execute('SELECT SUM(likes) as total_likes FROM videos WHERE user_id = ?', (user_id,)).fetchone()['total_likes'] or 0
    # Followers
    followers = db.execute('SELECT COUNT(*) as total_followers FROM followers WHERE following_id = ?', (user_id,)).fetchone()['total_followers'] or 0
    # Following
    following = db.execute('SELECT COUNT(*) as total_following FROM followers WHERE follower_id = ?', (user_id,)).fetchone()['total_following'] or 0
    # Subscribers (if you have a subscribers table, else use followers)
    subscribers = followers
    return {
        'likes': likes,
        'followers': followers,
        'following': following,
        'subscribers': subscribers
    }
