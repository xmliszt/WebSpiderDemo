# for getting song link from youtube
from utils.general_utils import fuzzy_validate
from utils.general_utils import keyword_validate
from utils.general_utils import link_validate
from utils.general_utils import memo_generator
from utils.general_utils import duplicate_validate
from utils.general_utils import metadata_search
from utils.general_utils import make_directory
import utils.constants as c
from time import sleep
from utils.log_manager import log_manager
import random
from copy import copy


youtube_logger = log_manager("youtube_processor")


def get_song(artist, title, browser, genre):
    """
    take artist and title string and output youtube link found
    :param artist: string
    :param title: string
    :param browser: chrome browser activated by selenium
    :param genre: current genre for memo naming
    :return: title, link, score, duration
    """

    try:
        query = ('\"' + artist + '\"' + " " + title)
        sleep(random.randint(5, 10))
        browser.get("https://www.youtube.com/results?search_query={}".format(query))
        found_vid = browser.find_elements_by_xpath('//a[@id="video-title"]')
        found_des = browser.find_elements_by_id("description-text")

        try:
            for vid in found_vid:
                vid_ind = found_vid.index(vid)
                title = vid.get_attribute("title")
                description = found_des[vid_ind].text
                tandd = title + " " + description
                fuzzy_score = fuzzy_validate(query.lower(), tandd.lower())
                f, m = keyword_validate(title.lower(), c.DANGER_WORDS)
                __link = vid.get_attribute('href')
                is_video = link_validate(__link, "video")
                duration = metadata_search(__link, 'duration')['duration']  # in seconds
                percentage_of_danger = f/(f+m)
                make_directory("src/memo")
                if percentage_of_danger == 0 and fuzzy_score >= c.FUZZ_THRESHOLD and is_video:
                    make_directory("src/memo/{}".format(genre))
                    if duplicate_validate(title, "src/memo/{}/memo_{}.txt".format(genre, artist)):
                        youtube_logger.warn("{} is duplicated. Skipped...".format(title))
                        continue
                    memo_generator(f"{title}\n", "src/memo/{}/memo_{}.txt".format(genre, artist))
                    youtube_logger.info("-------- {} is picked. --------".format(title))
                    return vid.get_attribute('href'), fuzzy_score, title, duration
                else:
                    continue
            return 'NOT FOUND', 0, None, 0
        except Exception as e:
            youtube_logger.error("Something wrong with selenium process. Error: {}".format(e))
            return 'ERROR', 0, None, 0
    except Exception as e:
        youtube_logger.error(str(e))
        return 'ERROR', 0, None, 0


def get_song_for_classical(query, browser, genre):
    """
    take artist and title string and output youtube link found
    :param query: query string to be searched
    :param browser: chrome browser activated by selenium
    :param genre: current genre for memo naming
    :return: title, link, score, duration
    """

    try:
        browser.get("https://www.youtube.com/results?search_query={}".format(query))
        found_vid = browser.find_elements_by_xpath('//a[@id="video-title"]')
        found_des = browser.find_elements_by_id("description-text")

        try:
            _duration_tolerance = copy(c.DURATION_TOLERANCE)
            for vid in found_vid:
                vid_ind = found_vid.index(vid)
                title = vid.get_attribute("title")
                description = found_des[vid_ind].text
                tandd = title + " " + description
                fuzzy_score = fuzzy_validate(query.lower(), tandd.lower())
                f, m = keyword_validate(title.lower(), c.DANGER_WORDS)
                __link = vid.get_attribute('href')
                is_video = link_validate(__link, "video")
                percentage_of_danger = f/(f+m)
                make_directory("src/memo")
                if percentage_of_danger == 0 and fuzzy_score >= c.FUZZ_THRESHOLD and is_video:
                    state, score = duplicate_validate(query+"\n", "src/memo/{}.txt".format(genre))
                    result_state, result_score = duplicate_validate(title+"\n", "src/memo/{}_result.txt".format(genre))
                    print(score, result_score)
                    if result_state or state*result_state:
                        youtube_logger.warn("{} is duplicated. Skipped...".format(title))
                        return "skipped", 0, None, 0
                    else:
                        duration = metadata_search(__link, 'duration')['duration']  # in seconds
                        if duration > 1200:
                            youtube_logger.warn("{} is too long. Skipped...".format(title))
                            continue
                        else:
                            # PICK THE SONG HERE !!!
                            memo_generator(f"{query}\n", "src/memo/{}.txt".format(genre))
                            memo_generator(f"{title}\n", "src/memo/{}_result.txt".format(genre))
                            youtube_logger.info("-------- {} is picked. --------".format(title))
                            return vid.get_attribute('href'), fuzzy_score, title, duration
                else:
                    continue
            return 'NOT FOUND', 0, None, 0
        except Exception as e:
            youtube_logger.error("Something wrong with selenium process. Error: {}".format(e))
            return 'ERROR', 0, None, 0
    except Exception as e:
        youtube_logger.error(str(e))
        return 'ERROR', 0, None, 0
