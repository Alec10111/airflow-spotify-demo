import os
from dotenv import load_dotenv

load_dotenv()

X_RAPIDAPI_KEY = os.getenv('X_RAPIDAPI_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
