from utils.log_manager import log_manager
import utils.constants as c
import requests
import urllib.request
import urllib.parse
import csv
import json
import youtube_dl
import os
import re
from fuzzywuzzy import fuzz
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from pykakasi import kakasi
from random import randint
from time import sleep


logger = log_manager("general_utils")


class XlsxWorkbook:

    xlsx_config = {
        'constant_memory': True,
        'tempdir': 'temp/xlsx'
    }

    def __init__(self, file_path):
        make_directory("temp/xlsx")
        self.workbook = xlsxwriter.Workbook(file_path+".xlsx", self.xlsx_config)
        self.q = ""

    def create_worksheet(self, name_of_worksheet):
        try:
            worksheet = self.workbook.add_worksheet(name_of_worksheet)
            return worksheet
        except Exception as e:
            logger.error("Failed to create worksheet! {}".format(e))
            return None

    def q_to_sum_cells_across_worksheets(self, worksheet_cells):
        """
        update query string to sum all cells
        :param worksheet_cells: a dictionary of <worksheet name>:<list of cells>
        :return: query string
        """

        for worksheet in worksheet_cells:
            if not isinstance(worksheet_cells[worksheet], list):
                raise TypeError("value in the worksheet_cells dictionary must be list")
            for cell in worksheet_cells[worksheet]:
                if isinstance(cell, tuple):
                    cell = xl_rowcol_to_cell(cell[0],cell[1])
                self.q += "'{}'!{}+".format(worksheet, cell)
        self.q = self.q[:-1]  # remove the last plus sign
        return self.q

    def write_in_summary(self, ws):
        bold = self.workbook.add_format({'bold': True})
        ws.set_column(0, 0, 25)
        ws.write('A1', "TOTAL COUNT:")
        ws.write_formula('B1', "={}".format(self.q))
        ws.write('A3',
                 'This count indicates the total number of songs found that are not with any labels, which are probably the correct ones!')
        ws.write_rich_string('A4',
                             'For the formula to count correctly, for any picked songs, please leave it blank under the',
                             bold,
                             '"Status"',
                             'column')
        ws.write_string('A6', 'Status Labels:', bold)
        r = randint(80, 100)
        ws.write_string('A8', "DUPLICATE {}".format(r))
        ws.write_string('B8',
                        'means the song is probably a duplicate of a song picked previously, it has a probability of {}% that it is a duplicate'.format(
                            r))
        ws.write_string('A9', "REMIX")
        ws.write_string('B9', 'means the song is a remix, not original')
        ws.write_string('A10', "LIVE PERFORMANCE")
        ws.write_string('B10', 'means the song is a live version')
        ws.write_string('A11', "NOT FROM ARTIST")
        ws.write_string('B11', 'means the song is probably not by the artist but someone else')
        ws.write_string('A12', "COVER")
        ws.write_string('B12', 'means the song is a cover version')


    def create_summary(self):
        try:
            ws = self.create_worksheet("SUMMARY")
            return ws

        except Exception as e:
            logger.error("Failed to create SUMMARY! {}".format(e))

    def close(self):
        self.workbook.close()


def musiio_tracks_csv_reader(file, delimiter, id_column, title_column, artist_column):
    """
    read a csv file and extract columns
    :param file: csv file
    :param delimiter: seperator
    :param id_column: column index of id
    :param title_column: column index of song title
    :return: a dictionary of <id>:<song title>
    """
    final = list()

    try:
        with open(file, 'r', encoding='utf-8') as fh:
            reader = csv.reader(fh, delimiter=delimiter)
            for row in reader:
                try:
                    id = row[id_column]
                    title = row[title_column]
                    artist = row[artist_column]
                except Exception as e:
                    logger.error("column index must be an integer! " + str(e))
                output = dict()
                output['id'] = id
                output['title'] = title
                output['artist'] = artist
                final.append(output)
    except Exception as e:
        logger.error("Cannot find the csv file! " + str(e))

    return final


def txt_to_list(file, delimiter):
    """
    convert txt file to list, extract all entries based on delimiter
    :param file: path of txt file
    :param delimiter: separator between entries
    :return: list of entries in txt file | if error, return empty list
    """
    try:
        with open(file, 'r', encoding='utf-8') as fh:
            output = list()
            for line in fh.readlines():
                entries = line.split(delimiter)
                for entry in entries:
                    output.append(entry.strip())
            logger.info(txt_to_list.__name__ + "--SUCCESS")
            fh.close()
            return output
    except Exception as e:
        logger.error(txt_to_list.__name__ + "--FAILED " + str(e))
        return list()

def bulk_txt_processor(file, delimiter):
    """
    for processing one single text file containing mulitple genre
    txt format:

    <genre> artist1, artist2, artist3, ...

    :param file: a txt file
    :param delimiter: seperator
    :return: list of genre and create multiple temp files for each genre containing artists
    """
    try:
        make_directory("temp")
        with open(file, 'r', encoding='utf-8') as fh:
            output = list()
            for line in fh.readlines():
                genre = re.match(r'(.*)<(.*)>\s(.*)', line)[2]
                print(genre)
                artists = re.match(r'(.*)<(.*)>\s(.*)', line)[3].split(delimiter)
                print(artists)
                _index = 0
                while _index <= len(artists)//10:
                    selected_artists = artists[_index*10:(_index+1)*10]  # extract 10 artists each time
                    string_of_artists = ",".join(selected_artists)
                    with open(os.path.join('temp', f'{genre}_{_index+1}.txt'), 'w+', encoding='utf-8') as f:
                        f.write(string_of_artists)
                        f.close()
                    output.append(f"{genre}_{_index+1}")
                    _index += 1
            fh.close()
            return output
    except Exception as e:
        logger.error("bulk processing failed! "+str(e))
        print(e)


def csv_writer_overwrite(path, *args):
    """
    overwrite a csv file
    :param path: path to the csv file
    :param args: any args to write in csv, in order in a row
    :return: None
    """
    try:
        with open(path, 'w+', encoding='utf-8', newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(args)
            logger.info(csv_writer_overwrite.__name__ + "--SUCCESS")
            fh.close()
    except Exception as e:
        logger.error(csv_writer_overwrite.__name__ + "--FAILED " + str(e))


def csv_writer_append(path, *args):
    """
    append a csv file
    :param path: path to the csv file
    :param args: any args to write in csv, in order in a row
    :return: None
    """
    try:
        with open(path, 'a+', encoding='utf-8', newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(args)
            logger.info(csv_writer_append.__name__ + "--SUCCESS")
            fh.close()
    except Exception as e:
        logger.error(csv_writer_append.__name__ + "--FAILED " + str(e))


def json_to_dict(j, local=True):
    """
    convert json to a dictionary file. JSON can be string or local file
    :param j: json string or file
    :param local: True if using local JSON file, False if using JSON string object
    :return: converted dictionary in a list. If failed return None
    """
    try:
        if local is True:
            with open(j, 'r', encoding='utf-8') as fp:
                json_dict = json.load(fp)
                logger.info(json_to_dict.__name__ + "--SUCCESS")
                fp.close()
                return json_dict
        else:
            json_dict = json.loads(j)
            logger.info(json_to_dict.__name__ + "--SUCCESS")
            return json_dict
    except Exception as e:
        logger.error(json_to_dict.__name__ + "--FAILED " + str(e))
        return None


def json_writer_overwrite(d, path):
    """
    overwrite a json file from dictionary
    :param d: dictionary to be written as json
    :param path: path to json file
    :return: None
    """
    try:
        with open(path, 'w+', encoding='utf-8') as fp:
            json.dump([d], fp)
            logger.info(json_writer_overwrite.__name__ + "--SUCCESS")
            fp.close()
    except Exception as e:
        logger.error(json_writer_overwrite.__name__ + "--FAILED " + str(e))


def json_writer_append(d, path):
    """
    append a json file from dictionary
    :param d: dictionary to be written as json
    :param path: path to json file
    :return: None
    """
    try:
        with open(path, 'r', encoding='utf-8') as fp:
            json_list = list(json.load(fp))
            json_list.append(d)
            fp.close()
        with open(path, 'w+', encoding='utf-8') as fs:
            json.dump(json_list, fs)
            logger.info(json_writer_append.__name__ + "--SUCCESS")
            fs.close()
    except Exception as e:
        logger.error(json_writer_append.__name__ + "--FAILED " + str(e))


def html_generator(url):
    """
    generate html file for web scraping from url
    :param url: target url
    :return: html markup object (input to beautifulsoup4)
    """
    try:
        fp = urllib.request.urlopen(url)
        html = fp.read()
        logger.info(html_generator.__name__ + "--SUCCESS")
        return html
    except Exception as e:
        logger.error(html_generator.__name__ + "--FAILED " + str(e))


def request_sender(url, **kwargs):
    """
    send request to target url and get response
    :param url: target url
    :param kwargs: all key-value pairs in params
    :return: response | if error: return None
    """
    try:
        r = requests.get(url, params=kwargs)
        logger.info(request_sender.__name__ + "--SUCCESS")
        return r
    except Exception as e:
        logger.error(request_sender.__name__ + "--FAILED " + str(e))
        return None


def metadata_search(link, *args):
    """
    get metadata from youtube song link

    Available args to choose from:

    id, title, url, ext, uploader, creator, license, release_date, timestamp,
    channel, channel_id, location, duration, view_count, like_count, dislike_count,
    repost_count, comment_count, average_rating, is_live, format, tbr, abr, acodec,
    asr, fps, container, filesize, filesize_approx, autonumber, playlist,
    playlist_index, playlist_id, playlist_title, playlist_uploader, playlist_uploader_id

    :param link: song link from youtube
    :param args: metadata features to be extracted
    :return: a dictionary of features from metadata of the target song
    """
    try:
        with youtube_dl.YoutubeDL(c.YDL_OPTS) as ydl:
            output = dict()
            sleep(randint(3, 4))
            dict_meta = ydl.extract_info(link, download=False)
            for arg in args:
                output[arg] = dict_meta[arg]
        logger.info(metadata_search.__name__ + "--SUCCESS")
        return output
    except Exception as e:
        logger.error(metadata_search.__name__ + "--FAILED " + str(e))
        return output


def query_generator(search_string):
    """
    parse search_string to be a html friendly format to be directly put into url
    :param search_string: string want to search in the search bar
    :return: parsed query string
    """
    try:
        query_string = urllib.parse.quote(search_string)
        return query_string
    except Exception as e:
        logger.error(query_generator.__name__ + "--FAILED " + str(e))
        return None


def fuzzy_validate(target, base):
    """
    a simple string matching validator which can set threshold
    :param target: the target string you want to use to compare
    :param base: the string that you want the target to compare with
    :return: fuzzy score out of 100
    """
    try:
        score = fuzz.token_set_ratio(base, target)
        return score
    except Exception as e:
        logger.error(fuzzy_validate.__name__ + "--FAILED " + str(e))
        return None


def link_validate(target_link, validation):
    """
    check if link points to a video
    :param target_link: youtube link
    :param validation: type of validation (playlist, video...)
    :return: True if correct | False if wrong
    """
    if validation == "playlist":
        if 'watch' in target_link and 'list' in target_link:
            return True
        else:
            return False
    elif validation == "video":
        if 'watch' in target_link and 'list' not in target_link and 'channel' not in target_link:
            return True
        else:
            return False
    else:
        logger.error("validation type does not exist!")


def keyword_validate(target, keywords):
    """
    absolute matching to see if keywords are present in target
    :param target: the target string in which you want to find keywords
    :param keywords: a list of keywords you want to find in the target
    :return: a tuple of two number indicating number of found keywords
             and not found keywords (found,not-found)
    """
    found = 0
    miss = 0

    try:
        for keyword in keywords:
            if keyword in target:
                found += 1
            else:
                miss += 1

        return found, miss
    except Exception as e:
        logger.error(keyword_validate.__name__ + "--FAILED " + str(e))
        return None


def memo_generator(entry, output_path):
    """
    write entry into txt file as memo, same path will append to memo
    :param entry: string want to store
    :param output_path: path to store this memo
    :return: None
    """
    try:
        with open(output_path, 'a+', encoding='utf-8') as fp:
            fp.write(entry)
            fp.close()
    except Exception as e:
        logger.error("Invalid output path. Error: {}".format(e))


def memo_validate(target, memo_path):
    """
    check if target present in memo in the memo_path
    :param target: target to check presence
    :param memo_path: path to store the memo
    :return: True if present | False if not present
    """
    try:
        with open(memo_path, 'r', encoding="utf-8") as fp:
            contents = fp.readlines()
            if target in contents:
                fp.close()
                return True
            else:
                fp.close()
                return False
    except Exception as e:
        logger.error("Cannot find main memo! Error: {}".format(e))
        return False


def duplicate_validate(target, memo_path):
    """
    check if song title extracted has alr existed in the memo (a differrent memo)
    :param target: song title extracted
    :param memo_path: memo that stores past song titles
    :return: True if present | False if not present
    """
    try:
        with open(memo_path, 'r', encoding="utf-8") as fp:
            contents = fp.readlines()
            for line in contents:
                score = fuzzy_validate(target, line)
                if score >= c.DUPLICATE_THRESHOLD:
                    logger.warn(f"Score: {score} | Target: {target} | Line: {line}")
                    fp.close()
                    return True, score
                else:
                    fp.close()
            return False, 0
    except Exception as e:
        logger.error("Cannot find search duplicate memo! Error: {}".format(e))
        return False, 0


def is_intitle(keyword, song_title):
    """
    check if keyword is in the song_title
    :param keyword: keyword
    :param song_title: song title
    :return: True if in title, False if not in title
    """
    if fuzz.partial_ratio(song_title, keyword) > c.INTITLE_THRESHOLD:
        return True
    else:
        return False


def is_best_match(keyword, song_title):
    """
    check if query string match search result
    :param keyword: keyword
    :param song_title: song title
    :return: True if in title, False if not in title
    """
    if fuzz.partial_ratio(song_title, keyword) > c.TITLE_MATCH_THRESHOLD:
        return True
    else:
        return False


def chunk(lst, n):
    """
    split lst into even pieces, each contains n items
    :param lst: input list of items
    :param n: number of items per sub list
    :return: a list of sub-list of results
    """
    output = list()
    for i in range(0, len(lst), n):
        sublst = lst[i: i+n]
        output.append(sublst)
    return output


def make_directory(directory):
    """
    check existing or make new directory
    :param directory: directory to check or create
    :return: None
    """
    if os.path.exists(directory):
        return None
    else:
        os.mkdir(directory)
        return None


def get_urlpic(url, id, out_path, pic_format):
    """
    given picture url and song id, output picture
    :param url: url of the picture
    :param id: id of the song
    :param out_path: output path for the image, the folder name
    :param pic_format: output extension of the picture, use ".png" for example
    :return: None
    """
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    path = os.path.join(out_path, f"{id}"+pic_format)
    urllib.request.urlretrieve(url, path)


def convert_japanese(j):
    """
    convert japanese to romaji
    :param j: unicode string
    :return: romaji conversion
    """
    k = kakasi()
    k.setMode('J', 'a')
    converter = k.getConverter()
    try:
        result = converter.do(j)
    except Exception as e:
        logger.error("Cannot convert Japanese. Skip...")
        result = j
    return result