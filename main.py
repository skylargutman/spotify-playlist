import os

import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy import oauth2
import dotenv

dotenv.load_dotenv()

song_list_date = input("What year do you want to travel to? Enter the date in this format YYYY-MM-DD: ")

url = f"https://www.billboard.com/charts/hot-100/{song_list_date}/"

headers = {
    'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

response = requests.get(url=url, headers=headers, )
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.select("div.o-chart-results-list-row-container")
song_list = [ [
    int(row.select("li.o-chart-results-list__item > span.c-label")[0].text.strip()),
    row.select("li.o-chart-results-list__item h3#title-of-a-story")[0].text.strip(),
    row.select("li.o-chart-results-list__item h3#title-of-a-story + span.c-label")[0].text.strip(),
] for row in rows]

scope = ["playlist-modify-private","playlist-modify-public"]

auth_manager = oauth2.SpotifyOAuth(
    scope=scope,
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri="https://example.org/callback"
)

sp = spotipy.Spotify(auth_manager=auth_manager)

user = sp.me()

song_uri_list = []
for song in song_list:
    track = sp.search(q=f"track:{song[1]} year:{song_list_date.split('-')[0]} artist:{song[2]}", type=["track"])
    if len(track["tracks"]["items"]) > 0:
        song_uri = track["tracks"]["items"][0]["uri"]
        song_uri_list.append(song_uri)
        print(song_uri)


playlist_id = sp.user_playlist_create(user=user["id"], name=f"{song_list_date} Billboard 100")

sp.playlist_add_items(playlist_id["id"], song_uri_list)

