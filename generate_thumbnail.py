import subprocess
import os

def generate_thumbnail(video_path, thumbnail_path):
    """
    Generate a JPG thumbnail from the video at 1 second mark using ffmpeg.
    """
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    try:
        # Use -ss before -i for fast seek, and -frames:v 1 for compatibility
        result = subprocess.run([
            'ffmpeg',
            '-y',
            '-ss', '1',  # Fast seek to 1 second
            '-i', video_path,
            '-frames:v', '1',
            '-vf', 'scale=320:-1',
            '-q:v', '2',  # Good quality
            thumbnail_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"✅ Thumbnail saved at {thumbnail_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate thumbnail: {e.stderr.decode(errors='ignore')}")
        return False

def generate_video_thumbnail(video_path, clip_path):
    """
    Generate a short 5-second video preview (clip) starting at 1s using ffmpeg.
    Improved: -ss after -i for accurate seek, explicit video mapping, better error output.
    """
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    try:
        result = subprocess.run([
            'ffmpeg',
            '-y',
            '-i', video_path,   # -i before -ss for accurate seek
            '-ss', '1',
            '-t', '5',
            '-map', '0:v:0',    # Use first video stream
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-vf', 'scale=320:-1',
            '-an',              # Remove audio (optional, safer for videos without audio)
            clip_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"🎬 Video preview saved at {clip_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate video clip: {e.stderr.decode(errors='ignore')}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        video_path = sys.argv[1]
        thumbnail_path = sys.argv[2]
        generate_thumbnail(video_path, thumbnail_path)
    elif len(sys.argv) == 4 and sys.argv[1] == '--clip':
        video_path = sys.argv[2]
        clip_path = sys.argv[3]
        generate_video_thumbnail(video_path, clip_path)
    else:
        print("Usage:")
        print("  python generate_thumbnail.py <video_path> <thumbnail_path>")
        print("  python generate_thumbnail.py --clip <video_path> <clip_path>")
