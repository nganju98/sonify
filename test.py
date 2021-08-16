import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from tinydb import TinyDB, Query
import soco
from soco import SoCo
import time
import json


class VolumeChecker:

    def __init__(self, spotify: Spotify, sonosZoneName: str):
        self.db = TinyDB('db.json')
        self.spotify = spotify
        self.sonosZone: SoCo = self.getSonosZone(sonosZoneName)
        self.currentTrackId: str = None
        self.lastVolume = self.sonosZone.volume
        track = self.getCurrentlyPlaying()
        if (track is not None):
            trackId = track['item']['id']
            self.currentTrackId = trackId
            loudness = self.getLoudness(trackId)
            self.desiredVolume = round(self.sonosZone.volume + loudness)
        else:
            print("no track playing now")
            self.currentTrackId = None
            self.desiredVolume = round(self.sonosZone.volume - 10)
        print(f'Init: Desired volume= {self.desiredVolume}, '
              f'starting sonos vol={self.lastVolume}')

    def getLoudness(self, trackId: str):
        q = Query()
        results = self.db.table('tracks').search(q.trackId == trackId)
        if (len(results) > 0):
            return results[0]["loudness"]
        else:
            print("non-cached track: hitting audio analysis api")
            analysis = self.spotify.audio_analysis(trackId)
            loudness = analysis['track']['loudness']
            self.db.table('tracks').insert(
                {"trackId": trackId, "loudness": loudness})
            return loudness

    def getPlaylist(self, playlistId: str):
        return self.spotify.playlist(playlistId)

    def getTrack(self, trackId: str):
        return self.spotify.track(trackId)

    def getCurrentlyPlaying(self):
        return self.spotify.currently_playing()

    def getSonosZone(self, sonosZoneName: str) -> SoCo:
        myzone: SoCo = None
        try:
            zones = soco.discover()
            myzone: SoCo = list(filter(
                lambda x: x.player_name == sonosZoneName, zones))[0]
            self.db.table("ips").truncate()
            self.db.table("ips").insert({"ip": myzone.ip_address})
        except Exception as ex:
            print(f'Error with discovery, probably vpn: {ex}')
            ips = self.db.table("ips").all()
            if (len(ips) == 1):
                myzone = SoCo(ips[0]["ip"])
            else:
                print("No cached entry for zone, can't discover")
        print(f'Found {myzone.player_name} :: {myzone.volume}')
        return myzone

    def checkIfUserChangedVolume(self):
        if (self.lastVolume != self.sonosZone.volume):
            delta = self.sonosZone.volume - self.lastVolume
            self.desiredVolume = self.desiredVolume + delta
            self.lastVolume = self.sonosZone.volume
            print(f'changed desired volume by {delta} to now: '
                  f'{self.desiredVolume}')

    def adjustVolume(self):
        state = self.sonosZone.get_current_transport_info()
        if (state is not None
                and state['current_transport_state'] == 'PLAYING'):
            print('.', end='', flush=True)
            self.checkIfUserChangedVolume()

            track = self.getCurrentlyPlaying()
            if (track is not None):
                trackId = track['item']['id']
                if (self.currentTrackId != trackId):
                    self.currentTrackId = trackId
                    print(f'new track: {trackId} : {track["item"]["name"]}')
                    loudness = self.getLoudness(trackId)
                    self.lastVolume = round(self.desiredVolume - loudness)
                    print(f'track loudness = {loudness}, '
                          f'desired = {self.desiredVolume}, '
                          f'old vol = {self.sonosZone.volume}, '
                          f'setting vol to {self.lastVolume}')
                    self.sonosZone.volume = self.lastVolume
        else:
            print('/', end='', flush=True)


def spotifyScratch():
    authMgr = SpotifyOAuth(client_id=os.environ.get("CLIENT_ID"),
                           client_secret=os.environ.get("CLIENT_SECRET"),
                           redirect_uri="http://127.0.0.1:4356",
                           scope="user-read-currently-playing "
                                 "user-library-read"
                           )

    checker = VolumeChecker(
        spotipy.Spotify(auth_manager=authMgr),
        os.environ.get("SONOS_ZONE")
        )

    while True:
        checker.adjustVolume()
        time.sleep(2)

    # track = checker.getCurrentlyPlaying()
    # print(json.dumps(track))
    # results = sp.current_user_saved_tracks()
    # for idx, item in enumerate(results['items']):
    #    track = item['track']
    #    print(idx, track['artists'][0]['name'], " – ", track['name'])
    # kaiPlaylistId =
    # playlist = checker.getPlaylist(kaiPlaylistId)
    # songs = playlist['tracks']['items']
    # song = songs[0]

    # for song in songs:
    #     #track = checker.getTrack(song['track']['id'])
    #     #print (track['name'])
    #     loudness = checker.getLoudness(song['track']['id'])
    #     print (f'{song["track"]["name"]} :: {loudness}' )
    # track = checker.getCurrentlyPlaying()
    # print ("*************************")
    # #print (track)
    # name = track['item']['name']
    # id = track['item']['id']
    # print (name)
    # loudness = checker.getLoudness(track['item']['id'])
    # print (loudness)
    # analysis = sp.audio_analysis(track['item']['id'])
    # print (analysis['track']['loudness'])
    # print ("****************")
    # print (analysis)


def sonosScratch():
    print("sonos")
    zones = soco.discover()
    myzone: SoCo = list(filter(
        lambda x: x.player_name == os.environ.get("SONOS_ZONE"),
        zones))[0]
    print(f'{myzone.player_name} :: {myzone.volume}')
    # myzone.volume = 18
    channel = myzone.get_current_transport_info()
    # myzone.state
    print(json.dumps(channel))


load_dotenv()
spotifyScratch()
# sonosScratch()
