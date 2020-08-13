from utils.playlist_search import youtube_playlist_search
from utils.general_utils import bulk_txt_processor
from utils.playlist_search import playlist_url_search
from utils.general_utils import json_to_dict
import os, time
import argparse

parser = argparse.ArgumentParser(description="Auto scrape songs from YouTube under given artist collections")

parser.add_argument('-p', '--primary', required=True, default="", help="set the primary genre, type: String")
parser.add_argument('-m', '--mode', required=False, default="DEFAULT", help="choose from DEFAULT, PLAYLIST, CONTINUOUS")
parser.add_argument('-i', '--input', required=True, default="", help="input path of the data file")
parser.add_argument('-g', '--genre', required=False, default="unknown", help="sub-genre name under the primary genre, not required for CONTINUOUS mode")

args = parser.parse_args()

primary = args.primary
mode = args.mode
input_path = args.input
genre = args.genre

'''
DEFAULT: one txt file contains one line of artists of any number separated by comma
PLAYLIST: provide particular playlist url with its associated artist name in a dictionary
CONTINUOUS: one txt file contains all the artists of a particular genre. Format being <genre> <artists...>, separated by comma
            programme will automatically select 10 artists in a batch to process
'''


if __name__ == '__main__':
    if mode == "CONTINUOUS":
        filenames = bulk_txt_processor(input_path, ',')
        for filename in filenames:
            path = os.path.join('temp', f"{filename}.txt")
            youtube_playlist_search(
                data=path,
                primary=primary,
                genre=filename
            )
            print("	※\(^o^)/※                     ※\(^o^)/※")
            print("	※\(^o^)/※    {} IS DONE!     	※\(^o^)/※".format(filename))
            print("	※\(^o^)/※ RESTING FOR 1 min 	※\(^o^)/※")
            print("	※\(^o^)/※                 	※\(^o^)/※")
            time.sleep(60)

    elif mode == "PLAYLIST":
        d_list = json_to_dict(input_path, local=True)
        playlist = dict()
        for d in d_list:
            correct_url = d['correction']
            artist = d['artist']
            playlist[artist] = correct_url

        playlist_url_search(
            artist_playlists=playlist,
            primary=primary,
            genre=genre
        )
    else:
        youtube_playlist_search(
            data=input_path,
            primary=primary,
            genre=genre
        )
