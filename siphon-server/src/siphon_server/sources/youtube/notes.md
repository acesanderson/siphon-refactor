Two options for metadata:

### YouTube Data API v3 (Official)
This is Google's official API that provides comprehensive metadata:

```python
from googleapiclient.discovery import build

# Requires API key from Google Cloud Console
youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')
request = youtube.videos().list(
    part='snippet,statistics',
    id='VIDEO_ID'
)
response = request.execute()
```

### yt-dlp (Most Popular Alternative)
This is probably your best bet - it's actively maintained and doesn't require API keys:
```python
import yt_dlp

def get_video_info(url):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title'),
            'uploader': info.get('uploader'),
            'view_count': info.get('view_count'),
            'duration': info.get('duration'),
            'upload_date': info.get('upload_date'),
            'description': info.get('description')
        }
```
