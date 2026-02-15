"""
PHASE 1: Fetch YouTube Videos and store in SQLite
Steps:
1. Connect to YouTube Data API v3
2. Get uploads playlist ID
3. Fetch the 20 most recent videos
4. Save to SQLite database
"""

import os
import sqlite3
import requests
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in .env file")
CHANNEL_ID = os.getenv('CHANNEL_ID', 'UCxUWIEL-USsiPak0Qy6_vVg')
MAX_VIDEOS = 20
BASE_URL = 'https://www.googleapis.com/youtube/v3'
DB_PATH = 'data/linguacopilot.db'


def get_uploads_playlist_id(channel_id, api_key):
    url = f'{BASE_URL}/channels?part=contentDetails&id={channel_id}&key={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['items'][0]['contentDetails']['relatedPlaylists']['uploads']


def fetch_videos(playlist_id, api_key, max_results=20):
    url = f'{BASE_URL}/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max_results}&key={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    videos = []
    for item in data['items']:
        videos.append({
            'id': item['snippet']['resourceId']['videoId'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'published_at': item['snippet']['publishedAt']
        })
    
    return videos


def save_to_db(videos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for video in videos:
        cursor.execute("""
        INSERT OR REPLACE INTO videos (id, title, description, published_at)
        VALUES (?, ?, ?, ?)
        """, (video['id'], video['title'], video['description'], video['published_at']))
    
    conn.commit()
    conn.close()


def main():
    print(f"🔍 Fetching videos from {CHANNEL_ID}...")
    
    playlist_id = get_uploads_playlist_id(CHANNEL_ID, YOUTUBE_API_KEY)
    print(f"✅ Playlist ID: {playlist_id}")
    
    videos = fetch_videos(playlist_id, YOUTUBE_API_KEY, MAX_VIDEOS)
    print(f"✅ {len(videos)} videos fetched")
    
    save_to_db(videos)
    print(f"✅ Saved to database")
    
    print("\n📺 Preview:")
    for i, v in enumerate(videos[:3], 1):
        print(f"  {i}. {v['title']}")


if __name__ == '__main__':
    main()