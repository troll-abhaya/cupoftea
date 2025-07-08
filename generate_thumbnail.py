import os
import sys
import ffmpeg

def generate_thumbnail(video_path, thumbnail_path):
    (
        ffmpeg
        .input(video_path, ss=1)
        .filter('scale', 320, -1)
        .output(thumbnail_path, vframes=1)
        .run(overwrite_output=True)
    )

if __name__ == "__main__":
    video_path = sys.argv[1]
    thumbnail_path = sys.argv[2]
    generate_thumbnail(video_path, thumbnail_path)
