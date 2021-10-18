from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import  load_dotenv
import os

load_dotenv()

choose_date = input("Which year do you want to travel to? Write the date in this format, YYYY-MM-DD:")

B_URL = f"https://www.billboard.com/charts/hot-100/{choose_date}"
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

response = requests.get(B_URL)
billboard_website = response.text

soup = BeautifulSoup(billboard_website, "html.parser")

top_songs = [music.getText() for music in soup.find_all(name="span", class_="chart-element__information__song "
                                                                            "text--truncate color--primary")]
artist_names = [artist.getText() for artist in soup.find_all(name="span", class_="chart-element__information__artist "
                                                                                 "text--truncate color--secondary")]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path=".cache",
    )
)
user_id = sp.current_user()["id"]

uri_list = []

for song in top_songs:
    song_info = sp.search(q=f"track:{song} year:{choose_date.split('-')[0]}", type="track")
    try:
        song_uri = song_info['tracks']['items'][0]['uri']
        uri_list.append(song_uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")


new_playlist = sp.user_playlist_create(user_id,
                                       f"{choose_date} Billboard 100",
                                       public=False, collaborative=False,
                                       description="Billboard 100 playlist")
playlist_id = new_playlist['id']

playlist_result = sp.playlist_add_items(playlist_id, uri_list)
