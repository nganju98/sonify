
from socket import SocketIO
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import tinydb
from tinydb import TinyDB, Query
import soco
from soco import SoCo
import time
import datetime

class VolumeChecker:

    def __init__ (self, spotify : Spotify, sonosZoneName : str) :
        print ("init")
        self.spotify = spotify
        self.sonosZone : SoCo = self.getSonosZone(sonosZoneName)
        self.currentTrackId : str = None
        self.db = TinyDB('db.json')

    def getLoudness(self, trackId : str)  : 
        q = Query()
        results = self.db.table('tracks').search(q.trackId == trackId)
        if (len(results) > 0) :
            return results[0]["loudness"]
        else :
            analysis = self.spotify.audio_analysis(trackId)
            loudness = analysis['track']['loudness']
            self.db.table('tracks').insert({"trackId":trackId, "loudness":loudness})
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
        print (f'checking at {datetime.datetime.now()}')
        track = self.getCurrentlyPlaying()
        trackId = track['item']['id']
        if (self.currentTrackId != trackId):      
            self.currentTrackId = trackId      
            print (f'new track: {trackId} : {track["item"]["name"]}')
            loudness = self.getLoudness(trackId)
            current = self.getDesiredVolume()
            volume  = round(current - loudness)
            print (f'track loudness = {loudness}, current = {current}, old vol = {self.sonosZone.volume}, setting vol to {volume}')        
            self.sonosZone.volume = volume


def spotifyScratch():
    checker = VolumeChecker(spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:4356",
    scope="user-read-currently-playing user-library-read")), os.environ.get("SONOS_ZONE"))

    while True:
        checker.adjustVolume()
        time.sleep(2)

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




