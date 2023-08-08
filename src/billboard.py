import requests
import json
from datetime import datetime
import settings

url = "https://billboard-api2.p.rapidapi.com/billboard-200"



headers = {
	"X-RapidAPI-Key": settings.X_RAPIDAPI_KEY,
	"X-RapidAPI-Host": "billboard-api2.p.rapidapi.com"
}

def get_billboard_top_tracks() -> list:
    current_date = datetime.today().strftime('%Y-%m-%d')
    top_range = "1-10" # free tier hard limit

    querystring = {"date":current_date,"range":top_range}
    # response = requests.get(url, headers=headers, params=querystring).json()
    # print(response.json())

    with open("mocks/billboard_songs.json") as mock:
        response = json.load(mock)

    # return response
    return [ track for ranking, track in response["content"].items()]
    