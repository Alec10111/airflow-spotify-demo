import requests
import settings

BASE_URL = "https://api.spotify.com/v1"
headers = {"Authorization": f"Bearer {settings.SPOTIFY_ACCESS_TOKEN}"}

PLAYLIST_ID = "4l351m3ZtXc2ir88426v99"

top_tracks = ['7z3Q4j4HJDSOZtbR5rbYdG','04wmRKlU8lSjmYql1mt052','6jemILri7l5LuPhKs2nuXr','0vber253Le8WWt7gKorVe9','6Kc9FbBnrzq0AbKEPfNkMx']


def get_track_id(song_name: str, artist: str) -> str:
    url = f"{BASE_URL}/search?q=track:{song_name}%20artist:{artist}&type=track"
    response = requests.get(url, headers=headers).json()
    if "error" in response:
        return ""
    if response["tracks"]["total"] > 0:
        return response["tracks"]["items"][0]["id"]
     

def get_playlist_id(playlist_name: str) -> str:
    ...


def get_recommended_tracks():
    url = f"{BASE_URL}/recommendations?limit=5&seed_tracks=${','.join(top_tracks)}"

def update_playlist(song_list: list):
    url = f"{BASE_URL}/v1/playlists/${PLAYLIST_ID}/tracks?uris=${','.join(song_list)}"
    requests.post(url)