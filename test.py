
from socket import SocketIO
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import tinydb
import soco
from soco import SoCo

class VolumeChecker:

    def __init__ (self, spotify : Spotify, sonosZoneName : str) :
        print ("init")
        self.spotify = spotify
        self.sonosZone : SoCo = self.getSonosZone(sonosZoneName)
        

    def getLoudness(self, trackId : str)  : 
        analysis = self.spotify.audio_analysis(trackId)
        loudness = analysis['track']['loudness']
        return loudness

    def getPlaylist(self, playlistId : str) :
        return self.spotify.playlist(playlistId)

    def getTrack(self, trackId : str) :
        return self.spotify.track(trackId)

    def getCurrentlyPlaying(self) :
        return self.spotify.currently_playing()

    def getDesiredVolume(self) :
        return 8

    def setSonosVolume(self, volume : int) :
        print ("set volume")

    def getSonosZone(self, sonosZoneName : str) -> SoCo :
        zones = soco.discover()
        myzone : SoCo = list(filter(lambda x: x.player_name == sonosZoneName, zones))[0]
        print (f'Found {myzone.player_name} :: {myzone.volume}')        
        return myzone
        
    def adjustVolume(self) :
        track = self.getCurrentlyPlaying()
        loudness = self.getLoudness(track['item']['id'])
        current = self.getDesiredVolume()
        volume  = round(current - loudness)
        print (f'track loudness = {loudness}, current = {current}, old vol = {self.sonosZone.volume}, setting vol to {volume}')        
        self.sonosZone.volume = volume


def spotifyScratch():
    checker = VolumeChecker(spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:4356",
    scope="user-read-currently-playing user-library-read")), os.environ.get("SONOS_ZONE"))

    checker.adjustVolume()

    #results = sp.current_user_saved_tracks()
    #for idx, item in enumerate(results['items']):
    #    track = item['track']
    #    print(idx, track['artists'][0]['name'], " – ", track['name'])
    #kaiPlaylistId = 
    #playlist = checker.getPlaylist(kaiPlaylistId)
    #songs = playlist['tracks']['items']
    #song = songs[0]

    # for song in songs:
    #     #track = checker.getTrack(song['track']['id'])
    #     #print (track['name'])
    #     loudness = checker.getLoudness(song['track']['id'])    
    #     print (f'{song["track"]["name"]} :: {loudness}' )
        

    #track = checker.getCurrentlyPlaying()
    # print ("*************************")
    # #print (track)
    #name = track['item']['name']
    # id = track['item']['id']
    #print (name)
    #loudness = checker.getLoudness(track['item']['id'])
    #print (loudness)
    # analysis = sp.audio_analysis(track['item']['id'])
    # print (analysis['track']['loudness'])
    #print ("****************")
    #print (analysis)

def sonosScratch():
    print ("sonos")
    zones = soco.discover()
    myzone : SoCo = list(filter(lambda x: x.player_name == os.environ.get("SONOS_ZONE"), zones))[0]
    print (f'{myzone.player_name} :: {myzone.volume}')
    myzone.volume = 18


load_dotenv()
spotifyScratch()
#sonosScratch()




