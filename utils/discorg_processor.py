# for getting tracks under artists on Discorg
from utils.general_utils import request_sender
from utils.general_utils import json_to_dict
import utils.constants as c
from time import sleep
from utils.log_manager import log_manager


discorg_logger = log_manager("discorg_processor")


def get_artist_url(artist):
    """
    get artist_url containing reources of a given artist
    :param artist: artist name
    :return: artist ID on Discorg
    """
    try:
        __response = request_sender(c.DISCORG_API+"database/search",
                                    query=artist,
                                    type="artist",
                                    token=c.DISCORG_TOKEN)
        __response_dict = json_to_dict(__response.text, local=False)
        __results = __response_dict['results']
        __most_relevant = __results[0]
        __artist_url = __most_relevant['resource_url']
        return __artist_url
    except Exception as e:
        discorg_logger.error(str(e))
        return None

def get_artist_resources_url(artist_url):
    """
    get artist's resources as a list
    :param artist_url: url where we can find resources from this artist
    :return: a list of all resource_url from this artist
    """
    try:
        __output = list()

        __response = request_sender(artist_url+"/releases", per_page=500)
        __response_dict = json_to_dict(__response.text, local=False)
        __releases = __response_dict['releases']
        for i in __releases:
            __resource_url = i['resource_url']
            __output.append(__resource_url)
        return __output
    except Exception as e:
        discorg_logger.error(str(e))
        return None


def get_artist_songtitles(resource_list):
    """
    get artist's song titles as a list
    backup as stored in local
    :param resource_list: a list of resource urls from the artist
    :return: a list of song titles under the artist
    """
    __no_repeat_set = set()

    try:
        for resource_url in resource_list:
            __response = request_sender(resource_url)
            sleep(3)
            __response_dict = json_to_dict(__response.text, local=False)
            __tracklist = __response_dict['tracklist']
            for __track in __tracklist:
                __title = __track['title']
                __no_repeat_set.add(__title)

        return list(__no_repeat_set)
    except Exception as e:
        discorg_logger.error(str(e))
        return None


def discorg_processor(artists):
    """
    output a JSON object containing all songs found in Discorg under a particular artist
    store a local copy as backup
    :param artists: the list of artists to be processed
    :return: a JSON file containing all songs found in Discorg under a particular artist
    """
    __output = dict()

    try:
        for artist in artists:
            artist_url = get_artist_url(artist)
            artist_resources = get_artist_resources_url(artist_url)
            artist_songlist = get_artist_songtitles(artist_resources)
            __output[artist] = artist_songlist

        return __output
    except Exception as e:
        discorg_logger.error(str(e))
        return None


