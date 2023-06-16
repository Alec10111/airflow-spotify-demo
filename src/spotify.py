import requests
import settings

BASE_URL = "https://api.spotify.com/v1"
headers = {"Authorization": f"Bearer {get_token()}"}

def get_token():
    header = {"Content-Type: application/x-www-form-urlencoded"}
    response = requests.post(
        url="https://accounts.spotify.com/api/token", 
        data="grant_type=client_credentials&client_id={settings.SPOTIFY_CLIENT_ID}&client_secret={settings.SPOTIFY_CLIENT_SECRET}",
        headers=header
        ).json()
    return response["access_token"]



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
    top_tracks = ['7z3Q4j4HJDSOZtbR5rbYdG','04wmRKlU8lSjmYql1mt052','6jemILri7l5LuPhKs2nuXr','0vber253Le8WWt7gKorVe9','6Kc9FbBnrzq0AbKEPfNkMx']
    url = f"{BASE_URL}/recommendations?limit=5&seed_tracks=${','.join(top_tracks)}"

def update_playlist(song_list: list):
    PLAYLIST_ID = "4l351m3ZtXc2ir88426v99"
    url = f"{BASE_URL}/v1/playlists/${PLAYLIST_ID}/tracks?uris=${','.join(song_list)}"
    requests.post(url,headers=headers)