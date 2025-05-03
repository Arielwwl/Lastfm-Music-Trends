# Relevant libraries
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load your API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
HEADERS = {'User-Agent': 'GlobalMusicTrendsApp'}

## Pull relevant info and store as csv ##
# Top artists globally
def get_top_artists(limit = 50):
    params = {
        "method": "chart.gettopartists",
        "api_key": API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(BASE_URL, params = params, headers = HEADERS)
    data = response.json()["artists"]["artist"]
    df = pd.DataFrame([{
        "artist": item["name"],
        "listeners": int(item["listeners"]),
        "playcount": int(item["playcount"])
    } for item in data])
    df.to_csv(os.path.join(DATA_DIR, "top_artists.csv"), index = False)

# Top tracks globally
def get_top_tracks(limit = 50):
    params = {
        "method": "chart.gettoptracks",
        "api_key": API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(BASE_URL, params = params, headers = HEADERS)
    data = response.json()["tracks"]["track"]
    df = pd.DataFrame([{
        "track": item["name"],
        "artist": item["artist"]["name"],
        "listeners": int(item["listeners"] if "listeners" in item else None),
        "playcount": int(item["playcount"])
    } for item in data])
    df.to_csv(os.path.join(DATA_DIR, "top_tracks.csv"), index = False)

# Top tags globally
def get_top_tags(limit = 50):
    params = {
        "method": "chart.gettoptags",
        "api_key": API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(BASE_URL, params = params, headers = HEADERS)
    data = response.json()["tags"]["tags"]
    df = pd.DataFrame([{
        "tag": item["name"],
        "count": int(item["count"])
    } for item in data])
    df.to_csv(os.path.join(DATA_DIR, "top_genres.csv"), index = False)

# Top tags for each artist
def get_artist_tags(artists):
    all_tags = []
    for artist in artists:
        params = {
            "method": "artists.gettoptags",
            "api_key": API_KEY,
            "format": "json"
        }
        response = requests.get(BASE_URL, params = params, headers = HEADERS)
        tags = response.json().get("toptags", {}).get("tag", [])
        for tag in tags[:5]: # top 5 tags per artist
            all_tags.append({"artist": artist, "tag": tag["name"], "count": tag.get("count", 0)})
    df = pd.DataFrame(all_tags)
    df.to_csv(os.path.join(DATA_DIR, "artist_genres.csv"), index = False)

# Top artists in countries
def get_country_artists(countries, limit = 10):
    all_data = []
    for country in countries:
        params = {
            "method": "geo.gettopartists",
            "country": country,
            "api_key": API_KEY,
            "format": "json",
            "limit": limit
        }
        response = requests.get(BASE_URL, params = params, headers = HEADERS)
        data = response.json().get("topartists", {}).get("artist", [])
        for artist in data:
            all_data.append({
                "country": country,
                "artist": artist["name"],
                "listeners": int(artist["listeners"]),
                "playcount": int(artist["playcount"])
            })
    df = pd.DataFrame(all_data)
    df.to_csv(os.path.join(DATA_DIR, "country_artists.csv"), index = False)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "Data")
    os.makedirs(DATA_DIR, exist_ok = True)

    get_top_artists()
    get_top_tags()
    get_top_tracks()

    # to get the genres for the top artists we extracted
    top_artists_df = pd.read_csv("Data/top_artists.csv")
    get_artist_tags(top_artists_df["artist"].tolist())

    # to get the top artists for these countries
    countries = []
    get_country_artists(countries, limit = 100)
