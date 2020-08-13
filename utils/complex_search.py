from utils.general_utils import csv_writer_append
from utils.general_utils import txt_to_list
from utils.general_utils import json_writer_overwrite
from utils.general_utils import json_to_dict
from utils.general_utils import memo_generator
from utils.general_utils import memo_validate
from utils.spotify_processor import spotify_processor
from utils.youtube_processor import get_song
from utils.log_manager import log_manager
from utils.selenium_processor_utils import chrome_driver_setup
import os
from copy import deepcopy
import sys
from retrying import retry


main_logger = log_manager("main_song_extraction")


def get_songs_from_artist(genre, data_path, source):
    """
    get songs from artists listed in the data file
    :param genre: genre of interest
    :param data_path: txt filename containing list of aritsts under the genre of interest
    :param source: specify from which API you want to search for the songs e.g. "spotify"
    :return: collection of songs from artists in a dictionary
    """
    # check if backup exists
    if os.path.exists("src/backup/{}.json".format(genre)):
        try:
            collection = json_to_dict("src/backup/{}.json".format(genre))[0]
        except Exception as e:
            main_logger.error("Extract backup failed! Error: {}".format(e))
            sys.exit()
        main_logger.info("Found backup!")

    # backup not found, do spotify search and create new backup
    else:
        try:
            artists = txt_to_list(data_path, ",")
        except Exception as e:
            main_logger.error("txt_to_list failed! Error: {}".format(e))
            sys.exit()
        try:
            if source == "spotify":
                collection = spotify_processor(artists)
            else:
                collection = None
                main_logger.error("This program currently does not support {}".format(source))
            if collection is None:
                sys.exit()
        except Exception as e:
            main_logger.error("spotify_processor failed! Error: {}".format(e))
            sys.exit()

        main_logger.info("Spotify process finished.............")

        if not os.path.exists("src/backup/"):
            os.mkdir("src/backup/")

        try:
            json_writer_overwrite(collection,
                                  "src/backup/{}.json".format(genre))
        except Exception as e:
            main_logger.error("json writer failed. Error: {}".format(e))
            sys.exit()
        main_logger.info("Successfully written new backup to src/backup/{}.json".format(genre))
    return collection


def youtube_search(collection, source):
    """
    search songs on youtube and output as csv
    :param collection: collection of songs as dictionary format
    :param source: source where you get the songs from, for record purpose only
    :return: None
    """
    # chrome driver activated
    browser = chrome_driver_setup()

    # youtube search for query items and output results
    __is_updated = False
    for artist in collection:
        main_logger.warn("----------------Artist: {}-----------------".format(artist))
        __index = 1
        for song in collection[artist]:
            if song == "":
                continue
            if memo_validate(f"{artist}: {song}\n", "src/memo/memo.txt") and __is_updated is False:
                __index += 1
                continue
            __is_updated = True
            memo_generator(f"{artist}: {song}\n", "src/memo/memo.txt")
            song_link, score, song_title = get_song(artist, song, browser)
            try:
                csv_writer_append("results/{}.csv".format(artist),
                                  __index, f"\"{artist}\" {song}", song_title, song_link, score, source)
            except Exception as e:
                main_logger.error("csv failed to append! Error: {}".format(e))
            main_logger.info(
                "Search: {} Return: {} {} Score: {}".format(artist + " " + song, song_title, song_link, score))
            __index += 1


@retry(wait_random_min=1000, wait_random_max=3000, stop_max_attempt_number=20)
def complex_search(choice="all", genre="", data="", source=""):
    """
    perform entire song_extraction based on user's input
    :param choice: "gsfa": get song from artists | "all": get song from artists + youtube extraction
    :param genre: genre of a group of artists of interest, will become the name of backup file after gsfa
    :param data: input data file in txt containing artists under the genre of interest
    :param source: the API source where we get the songs from the artists, e.g. "spotify"
    :return: None
    """
    if genre == "":
        return "No genre is recognised! Please input a genre!"
    if data == "":
        return "Please enter a path of your input data file"
    if not data.endswith(".txt"):
        return "Please input a txt data file!"

    data_path = os.path.join("src/artists", data)

    if choice == "gsfa":
        get_songs_from_artist(genre, data_path, source)
    elif choice == 'all':
        collection = get_songs_from_artist(genre, data_path, source)

        # make a copy of backup for usage
        if collection is None:
            main_logger.error("Failed to create a collection for youtube search. Exit program...")
            sys.exit()
        else:
            collection_copy = deepcopy(collection)
            youtube_search(collection_copy, source)
    else:
        main_logger.error("This program currently does not support this choice: {}. "
                          "Available choices are: 'gsfa' and 'all'. ".format(choice))





