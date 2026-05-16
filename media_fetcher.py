import requests
import tempfile
from config import PIXABAY_API_KEY, PIXABAY_VIDEO_PER_PAGE, PIXABAY_MUSIC_PER_PAGE

PIXABAY_VIDEO_URL = "https://pixabay.com/api/videos/"
PIXABAY_MUSIC_URL = "https://pixabay.com/api/music/"

async def fetch_video_clips(keywords: list, min_duration: int = 3) -> list:
    """
    Search Pixabay for videos matching the keywords.
    Returns a list of local file paths (downloaded MP4 files).
    """
    query = " ".join(keywords)
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": PIXABAY_VIDEO_PER_PAGE,
        "min_duration": min_duration
    }
    response = requests.get(PIXABAY_VIDEO_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    video_paths = []
    for hit in data.get("hits", []):
        # Prefer medium or large videos, take first available
        videos = hit.get("videos", {})
        for quality in ["large", "medium", "small"]:
            if quality in videos:
                video_url = videos[quality]["url"]
                break
        else:
            continue
        
        # Download video
        resp = requests.get(video_url, stream=True)
        resp.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        for chunk in resp.iter_content(chunk_size=8192):
            tmp.write(chunk)
        tmp.close()
        video_paths.append(tmp.name)
    
    return video_paths

async def fetch_background_music(keywords: list, mood: str = "upbeat") -> str:
    """
    Search Pixabay music for a track matching the overall mood/keywords.
    Returns the path to the downloaded MP3 file.
    """
    query = f"{' '.join(keywords)} {mood}"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": PIXABAY_MUSIC_PER_PAGE
    }
    response = requests.get(PIXABAY_MUSIC_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    hits = data.get("hits", [])
    if not hits:
        raise Exception("No music found for the given query.")
    
    music_url = hits[0].get("audio", "")
    if not music_url:
        raise Exception("Music track has no audio URL.")
    
    resp = requests.get(music_url, stream=True)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    for chunk in resp.iter_content(chunk_size=8192):
        tmp.write(chunk)
    tmp.close()
    return tmp.name