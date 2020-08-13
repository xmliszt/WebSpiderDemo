import utils.constants as c
from utils.general_utils import txt_to_list
from utils.general_utils import json_writer_overwrite
from utils.spotify_processor import spotify_processor
from utils.log_manager import log_manager
import os

logger = log_manager("artist_song_extraction")


def artist_song_extraction():
    try:
        artists = txt_to_list(c.INPUT, ",")
    except Exception as e:
        artists = None
        logger.error("txt_to_list failed! Error: {}".format(e))
    try:
        collection = spotify_processor(artists)
    except Exception as e:
        collection = None
        logger.error("spotify_processor failed! Error: {}".format(e))
    logger.info("Spotify process finished.............")

    if not os.path.exists("src/backup/"):
        os.mkdir("src/backup/")

        try:
            json_writer_overwrite(collection,
                                  "src/backup/{}.json".format(c.GENRE))
        except Exception as e:
            logger.error("json writer failed. Error: {}".format(e))
        logger.info("Write new backup to src/backup/{}.json".format(c.GENRE))