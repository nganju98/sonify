
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()
print (os.environ.get("CLIENT_ID"))
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ.get("CLIENT_ID"),
                                               client_secret=os.environ.get("CLIENT_SECRET"),
                                               redirect_uri="http://127.0.0.1:4356",
                                               scope="user-read-currently-playing user-library-read"))

#results = sp.current_user_saved_tracks()
#for idx, item in enumerate(results['items']):
#    track = item['track']
#    print(idx, track['artists'][0]['name'], " – ", track['name'])
kaiPlaylistId = '2QvfLfXL0L0BNVZYF3bF9F'
playlist = sp.playlist(kaiPlaylistId)
songs = playlist['tracks']['items']
#song = songs[0]

# for song in songs:
#     #track = sp.track(id)
#     #print (track['name'])
#     analysis = sp.audio_analysis(song['track']['id'])
#     print (song['track']['name'])
#     print (analysis['track']['loudness'])

track = sp.currently_playing()
print ("*************************")
#print (track)
name = track['item']['name']
id = track['item']['id']
print (name)
analysis = sp.audio_analysis(track['item']['id'])
print (analysis['track']['loudness'])
#print ("****************")
#print (analysis)