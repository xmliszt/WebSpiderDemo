from utils.selenium_processor_utils import chrome_driver_setup
from utils.general_utils import txt_to_list
from utils.general_utils import csv_writer_append
from utils.spotify_processor import get_artist_id
from utils.spotify_processor import get_artist_albums_classical
from utils.spotify_processor import get_album_tracks
from utils.youtube_processor import get_song_for_classical
from utils.log_manager import log_manager
from utils.general_utils import make_directory
from time import sleep
from random import randint


logger = log_manager("classical_search")


def classical_search(data, primary, genre):
    """
    to get song under a particular genre under primary using song-by-song search method
    :param data: txt file containing artists of the genre
    :param primary: primary genre for folder creation
    :param genre: genre that the list of artists belong to
    :return: None
    """
    __counter = 0  # count total number of songs get
    __browser = chrome_driver_setup()

    # read data file, extract list of artists
    artists = txt_to_list(data, delimiter=',')

    # for each artist, find artist id and then output list of album names
    __index = 0
    make_directory("results/{}".format(primary))
    filecount = 0
    while filecount <= len(artists)//10:
        print("========== Starting for batch {} - {} ==========".format(filecount*10,(filecount+1)*10))
        for artist in artists[filecount*10:(filecount+1)*10]:
            print("                 NOW FOR ARTIST: {}            ".format(artist))
            aid = get_artist_id(artist)
            if aid is None:
                print("Cannot find artist {} in Spotify.".format(artist))
                continue
            album_ids = get_artist_albums_classical(aid)
            for album in album_ids:
                tracks = get_album_tracks(album, 'name')
                if tracks is None:
                    print("Artist {} has no album found in Spotify.".format(artist))
                    continue
                for track in tracks:
                    if track is None or track == "":
                        print("Empty track, skip...")
                        continue
                    print("Current track: {}".format(track))
                    sleep(randint(3, 5))
                    __index += 1
                    link, score, title, duration = get_song_for_classical(track, __browser, genre)
                    if link == "skipped":
                        print("Duplicate, skip...")
                        continue
                    csv_writer_append("results/{}/{}_{}.csv".format(primary, genre, filecount+1),
                                      __index,
                                      track,
                                      title,
                                      link,
                                      score,
                                      duration)
                    print("{} -- CSV done: {} {} {} {}".format(__index, title, link, score, duration))
                    print("")
        print("||||||||||| Finished for batch {} - {} |||||||||||".format(filecount*10,(filecount+1)*10))
        filecount += 1
