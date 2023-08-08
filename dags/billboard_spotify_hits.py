import datetime
import pendulum
import os

import requests
import pandas as pd
from sqlalchemy import create_engine


from airflow import Dataset
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable


BASE_URL = "https://api.spotify.com/v1"


    # def get_spotify_token():
        
    #     SPOTIFY_CLIENT_ID = Variable.get("SPOTIFY_CLIENT_ID")
    #     SPOTIFY_CLIENT_SECRET = Variable.get("SPOTIFY_CLIENT_SECRET")

        
    #     header = {"Content-Type": "application/x-www-form-urlencoded"}
        
    #     data = {
    #         "grant_type": "client_credentials",
    #         "client_id": SPOTIFY_CLIENT_ID,
    #         "client_secret": SPOTIFY_CLIENT_SECRET,
    #         "scope": "playlist-modify-public" 
    #     }

    #     response = requests.post(
    #         url="https://accounts.spotify.com/api/token", 
    #         data=data,
    #         headers=header
    #         ).json()

    #     print(response)
    #     return response["access_token"]

def get_spotify_token():
    CLIENT_ID = Variable.get("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = Variable.get("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = 'http://localhost:3000/callback'  # Replace with your redirect URI
    # Step 1: Get the authorization code without user interaction (only need to run once)
    auth_url = 'https://accounts.spotify.com/authorize'
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'playlist-modify-public',  # Add any additional scopes you need
    }
    auth_response = requests.get(auth_url, params=auth_params)
    authorization_code = auth_response.url.split('code=')[1]

    # Step 2: Exchange the authorization code for an access token and refresh token
    token_url = 'https://accounts.spotify.com/api/token'
    token_params = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(token_url, data=token_params)
    response_data = response.json()

    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')

    return access_token

def get_track_id(song_name: str, artist: str) -> str:
    SPOTIFY_TOKEN = get_spotify_token()
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {SPOTIFY_TOKEN}"
    }
    search_params = {
        'q': f'track:{song_name} artist:{artist}',
        'type': 'track',
        'limit': 1
    }

    url = f"{BASE_URL}/search"
    # print(url)
    response = requests.get(url,params=search_params, headers=headers).json()
    # print("Get Track Response ==========================")
    # print(response)
    if "error" in response:
        return None
    if response["tracks"]["total"] > 0:
        return response["tracks"]["items"][0]["id"]
     
def update_playlist(song_list: list):
    SPOTIFY_TOKEN = get_spotify_token()
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {SPOTIFY_TOKEN}"
    }
    PLAYLIST_ID = "3Kwn4ayTCBm13atyTIhll5"
    url = f"{BASE_URL}/playlists/{PLAYLIST_ID}/tracks?uris={','.join(song_list)}"
    print(url)
    requests.put(url,headers=headers)


@dag(
    dag_id="billboard_spotify_hits",
    schedule_interval="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def BillboardSpotifyHits():

    create_billboard_table = PostgresOperator(
        task_id="create_billboard_table",
        postgres_conn_id="billboard_spotify",
        sql="""
            CREATE TABLE IF NOT EXISTS billboard (
                rank INTEGER PRIMARY KEY,
                track_name TEXT,
                artist TEXT,
                last_week_rank INTEGER,
                peak_position INTEGER,
                weeks_on_chart INTEGER,
                detail TEXT
                );
        """,
    )

    create_genius_table = PostgresOperator(
        task_id="create_genius_table",
        postgres_conn_id="billboard_spotify",
        sql="""
            CREATE TABLE IF NOT EXISTS genius(
                current_rank INTEGER,
                track_name TEXT,
                artist TEXT,
                last_week_rank INTEGER,
                peak_position INTEGER,
                weeks_on_chart INTEGER,
                detail TEXT,
                PRIMARY KEY(track_name, artist)
                );
        """,
    )

    create_spotify_table = PostgresOperator(
        task_id="create_spotify_table",
        postgres_conn_id="billboard_spotify",
        sql="""
            CREATE TABLE IF NOT EXISTS spotify (
                track_id TEXT PRIMARY KEY,
                current_rank INTEGER,
                track_name TEXT,
                artist TEXT,
                genres integer[],
                last_week_rank INTEGER,
                peak_position INTEGER,
                weeks_on_chart INTEGER,
                detail TEXT
                );
        """,
    )

    @task
    def get_billboard_data():

        X_RAPIDAPI_KEY = Variable.get("X_RAPIDAPI_KEY")

        url = "https://billboard-api2.p.rapidapi.com/billboard-200"
        
        today = datetime.date.today()
        weekday = today.weekday()  # Monday is 0 and Sunday is 6

        days_to_subtract = (weekday + 2) % 7  # Calculating the number of days to subtract
        last_saturday = today - datetime.timedelta(days=days_to_subtract)
        
        top_range = "1-10" # free tier hard limit
        querystring = {"date":last_saturday,"range":top_range}
        headers = {
	        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
	        "X-RapidAPI-Host": "billboard-api2.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring).json()

        # with open("/mocks/billboard_songs.json") as mock:
        #     response = json.load(mock)

        billboard_tracks = [ track for ranking, track in response["content"].items()]

        tracks_df = pd.DataFrame(billboard_tracks)
        engine = create_engine('postgresql://airflow:airflow@postgres:5432/bbsp')

        try:
            tracks_df.to_sql("billboard", engine,index=False, if_exists='replace')
        except:
            print("Idk mate, something went wrong")

    @task
    def update_spotify_playlist():
        SPOTIFY_TOKEN = get_spotify_token()
        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {SPOTIFY_TOKEN}"
        }

        # postgres_hook = PostgresHook(postgres_conn_id="billboard_spotify")
        # billboard_top_tracks = postgres_hook.get_records("billboard")
        engine = create_engine('postgresql://airflow:airflow@postgres:5432/bbsp')
        with engine.connect() as conn:
            billboard_top_tracks = pd.read_sql_query("SELECT * FROM billboard", conn )

        print(billboard_top_tracks)
        track_ids = []
        for song in billboard_top_tracks.iterrows():
            print("Songs from billboard songs")
            print(song)
            track_id = get_track_id(song_name=song[1][1], artist=song[1][2])
            if track_id:
                track_ids.append(track_id)

        print("Track id list", track_ids)

        update_playlist(track_ids)
    
    update_spotify_playlist()
        # [create_billboard_table, create_spotify_table] >> get_billboard_data() >> update_spotify_playlist()


dag = BillboardSpotifyHits()