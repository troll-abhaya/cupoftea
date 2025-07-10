import os
from generate_thumbnail import generate_thumbnail

VIDEO_DIR = os.path.join('static', 'videos')
THUMBNAIL_DIR = os.path.join('static', 'thumbnails')
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

video_extensions = {'.mp4', '.mov', '.avi', '.mkv'}

for filename in os.listdir(VIDEO_DIR):
    name, ext = os.path.splitext(filename)
    if ext.lower() not in video_extensions:
        continue
    video_path = os.path.join(VIDEO_DIR, filename)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{name}.jpg")
    if os.path.exists(thumbnail_path):
        print(f"Thumbnail already exists for {filename}, skipping.")
        continue
    try:
        print(f"Generating thumbnail for {filename}...")
        generate_thumbnail(video_path, thumbnail_path)
    except Exception as e:
        print(f"Failed to generate thumbnail for {filename}: {e}") 