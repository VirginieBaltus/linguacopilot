"""
PHASE 2: Download Subtitles
Steps:
1. Read videos.json
2. For each video, check if German subtitles exist
3. Download subtitles to data/raw/subtitles/
4. Skip videos without subtitles
"""

import os
import json
import yt_dlp

INPUT_FILE = 'data/raw/videos.json'
OUTPUT_DIR = 'data/raw/subtitles'


def download_subtitle(video_id, output_dir):
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': ['de'],
        'subtitlesformat': 'vtt',
        'outtmpl': f'{output_dir}/{video_id}.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    print(f"📥 Downloading subtitles for {len(videos)} videos...")
    
    success_count = 0
    for i, video in enumerate(videos, 1):
        video_id = video['id']
        title = video['title'][:50]
        
        if download_subtitle(video_id, OUTPUT_DIR):
            print(f"  ✅ {i}/{len(videos)} - {title}...")
            success_count += 1
        else:
            print(f"  ❌ {i}/{len(videos)} - {title} (no subtitles)")
    
    print(f"\n✅ Downloaded {success_count}/{len(videos)} subtitles")


if __name__ == '__main__':
    main()
