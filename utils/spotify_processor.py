import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import utils.constants as c
from utils.general_utils import chunk
from time import sleep
from utils.log_manager import log_manager

client_credentials_manager = SpotifyClientCredentials(client_id=c.SPOTIFY_CLIENTID,
                                                      client_secret=c.SPOTIFY_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

spotify_logger = log_manager("spotify_processor")


def get_metadata(track_id, *args):
    """
    get specific metadata of the track
    :param track_id:
    :param args:  https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/
    :return: dictionary of metadata
    """
    output = dict()
    metadata = sp.audio_features(track_id)[0]

    for arg in args.__iter__():
        output[arg] = metadata[arg]

    return output


def get_album_tracks(album_id, type):
    """
    get list of tracks in an album
    :param album_id: album id
    :param type: 'name' or 'id'
    :return: list of track in the album
    """
    tracks = list()
    try:
        response = sp.album_tracks(album_id=album_id,
                                   limit=50,
                                   offset=0)
        items = response['items']
        if type == 'name':
            for track in items:
                track_name = track['name']
                track_name = "".join(track_name.split(":")[:-1])
                if track_name in tracks:
                    continue
                else:
                    tracks.append(track_name)
            spotify_logger.info("Found tracks: {}".format(tracks))
            return tracks
        elif type == 'id':
            for track in items:
                track_id = track['id']
                if track_id in tracks:
                    continue
                else:
                    tracks.append(track_id)
            spotify_logger.info("Found tracks: {}".format(tracks))
            return tracks
        else:
            spotify_logger.error("Unknown type!")
            return []
    except Exception as e:
        spotify_logger.error("Filed to get tracks from album: {}  REASON: {}".format(album_id, e))


def get_artist_albums_classical(artist_id):
    """
    get albums of artist from id [special for classical]
    :param artist_id: artist id
    :return: list of album_ids under the artist
    """
    album_ids = list()
    __count = 0
    try:
        while True:
            if __count > c.MAX_ALBUM_NUMBER:
                break
            response = sp.artist_albums(artist_id=artist_id,
                                        album_type='album',
                                        limit=50,
                                        offset=0)
            items = response['items']
            for album in items:
                album_name = album['name']
                album_id = album['id']
                if "solo" not in album_name.lower():
                    album_ids.append(album_id)
                    __count += 1
            if response['next'] is None:
                break
        return album_ids
    except Exception as e:
        spotify_logger.error("Fail to get classical albums! Reason: {}".format(e))


def get_artist_id(artist):
    """
    get artist id from artist name
    :param artist: artist name
    :return: artist id
    """
    try:
        response = sp.search(q=artist.lower(),
                             type='artist',
                             limit=1)
        artist_id = response['artists']['items'][0]['id']
        return artist_id
    except Exception as e:
        spotify_logger.error("Can't seem to find the artist name! Reason: {}".format(e))


def get_artist_albums(artist_id):
    """
    get albums of artist from id
    :param artist_id: artist id
    :return: list of album_ids under the artist
    """
    multiplier = 0
    album_ids = list()
    __count = 0
    try:
        while True:
            if __count > c.MAX_ALBUM_NUMBER:
                break
            response = sp.artist_albums(artist_id=artist_id,
                                        album_type='album',
                                        limit=50,
                                        offset=multiplier*50)
            items = response['items']
            for album in items:
                album_id = album['id']
                album_ids.append(album_id)
                __count += 1
            if response['next'] is None:
                break
            else:
                multiplier += 1
        spotify_logger.info("Found albums: {}".format(album_ids))
        return album_ids
    except Exception as e:
        spotify_logger.error("Fail to get artist albums! Reason: {}".format(e))


def get_artist_tracks(album_ids):
    """
    get all track names under the artist in a list
    NOTE: spotify can't take too many ids at a time
    This function will split the albums ids in batch
    :param album_ids: album_ids list
    :return: list of all track names under the artist
    """
    track_list = list()
    chunks = chunk(album_ids, 10)
    try:
        for batch in chunks:
            sleep(10)
            response = sp.albums(batch)
            albums = response['albums']
            for album in albums:
                tracks = album['tracks']['items']
                for song in tracks:
                    track_title = song['name']
                    track_list.append(track_title)
        return track_list
    except Exception as e:
        spotify_logger.error("Fail to get artist tracks! Reason: {}".format(e))


def get_album_art(song_title):
    """
    search song title in spotify and return the album id the song is in
    :param song_title: song title in string
    :return: album art url of the song | None if not found
    """
    try:
        response = sp.search(q=song_title,
                             type='track')
        return response['tracks']['items'][0]['album']['images'][0]['url']

    except Exception as e:
        spotify_logger.error('Failed to find album id from {}. REASON: {}'.format(song_title, e))
        return None


def spotify_processor(artists):
    """
    output a JSON object containing all songs found in Spotify under a particular artist
    store a local copy as backup
    :param artists: the list of artists to be processed
    :return: a JSON file containing all songs found in Spotify under a particular artist
    """
    _output = dict()
    try:
        for artist in artists:
            spotify_logger.warn(f"----------------- {artist} -----------------")
            artist_id = get_artist_id(artist)
            spotify_logger.warn(f"                  get ID done                 ")
            album_ids = get_artist_albums(artist_id)
            spotify_logger.warn(f"                  get albums done                 ")
            track_list = get_artist_tracks(album_ids)
            spotify_logger.warn(f"                  get tracks done                 ")
            _output[artist] = track_list
        return _output
    except Exception as e:
        spotify_logger.error("Spotify processor failed! Reason: {}".format(e))
