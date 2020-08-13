from utils.selenium_processor_utils import chrome_driver_setup
from utils.selenium_processor_utils import scroll_down
from utils.general_utils import txt_to_list
from utils.general_utils import query_generator
from utils.general_utils import memo_generator
from utils.general_utils import duplicate_validate
from utils.general_utils import link_validate
from utils.general_utils import is_intitle
from utils.general_utils import is_best_match
from utils.general_utils import make_directory
from utils.general_utils import XlsxWorkbook
from utils.general_utils import json_writer_append
from utils.general_utils import json_writer_overwrite
from utils.general_utils import metadata_search
from utils.general_utils import convert_japanese
import utils.constants as c
from utils.log_manager import log_manager
import sys, os
from unidecode import unidecode


playlist_search_logger = log_manager("playlist_search")


def playlist_url_search(artist_playlists, primary, genre):
    """
    search for a particular playlist given the playlist url
    :param artist_playlists: a dictionary of <aritst>:<playlist_url>
    :param primary:
    :param genre:
    :return:
    """
    __browser = chrome_driver_setup()
    make_directory("results")
    make_directory("results/{}".format(primary))
    workbook_path = "results/{}/{}".format(primary, genre)
    workbook = XlsxWorkbook(workbook_path)
    print(" ============== NEW WORKBOOK: {}.xlsx =============\n".format(genre))
    summary = workbook.create_summary()  # create a summary page
    worksheet_cells = dict()
    for artist in artist_playlists:
        print("------------------- Writing Worksheet: {} -------------------".format(artist))
        if len(artist) > 25:
            _worksheet_name = artist[:20] + "..."
        else:
            _worksheet_name = artist
        _search_name = _worksheet_name.replace("'", "''")
        __browser.get(artist_playlists[artist])
        scroll_down(__browser, c.SCROLL_PAGE)
        contents = __browser.find_element_by_xpath('//div[@id="contents"]')
        song_lists = contents.find_elements_by_xpath(
            '//a[@class="yt-simple-endpoint style-scope ytd-playlist-video-renderer"]')
        __index = 1
        make_directory("src/memo/{}".format(genre))
        print("FOUND {} SONGS".format(len(song_lists)))
        artist_worksheet = workbook.create_worksheet(_worksheet_name)
        if artist_worksheet is None:
            print("|||||| Failed to create worksheet ||||||")
            sys.exit()
        artist_worksheet.set_column('A:A', 6)
        artist_worksheet.set_column('B:B', 18)
        artist_worksheet.set_column('C:C', 70)
        artist_worksheet.set_column('D:D', 100)
        artist_worksheet.set_column('E:E', 15)
        artist_worksheet.set_column('F:F', 100)
        artist_worksheet.write_row('A1', c.HEADER)
        _row_number = 0
        for song in song_lists:
            _row_number += 1
            song_link = song.get_attribute('href')

            if link_validate(song_link, "playlist"):
                song_title = song.find_element_by_id('video-title').get_attribute('title')
                try:
                    song_thumb = song.find_element_by_id('byline').find_element_by_tag_name('a').text.lower()
                except Exception:
                    song_thumb = ""
                check, score = duplicate_validate(song_title + "\n", "src/memo/{}/memo_{}.txt".format(genre, artist))
                print("++++++ Validating song: {} ++++++".format(song_title))
                input_sentence = song_title.lower() + " " + song_thumb
                j_converted = convert_japanese(input_sentence)
                uniconverted = unidecode(j_converted)
                if check:
                    playlist_search_logger.warn("DUPLICATE FOUND IN THE MEMO. REJECTED: {}".format(song_title))
                    status = "DUPLICATE {}".format(score)
                elif is_intitle("live", song_title.lower()):
                    playlist_search_logger.warn("LIVE PERFORMANCE. REJECTED: {}".format(song_title))
                    status = "LIVE PERFORMANCE"
                elif is_intitle("remix", song_title.lower()):
                    playlist_search_logger.warn("REMIX. REJECTED: {}".format(song_title))
                    status = "REMIX"
                elif is_intitle("cover", song_title.lower()):
                    playlist_search_logger.warn("SONG COVER. REJECTED: {}".format(song_title))
                    status = "COVER"
                elif not is_best_match(artist.lower(), uniconverted):
                    playlist_search_logger.warn("SONG TITLE DOES NOT CONTAIN ARTIST NAME. REJECTED: {}".format(song_title))
                    status = "NOT FROM ARTIST"
                else:
                    status = ""
                    memo_generator(song_title + "\n", "src/memo/{}/memo_{}.txt".format(genre, artist))
                artist_worksheet.write_row(_row_number, 0, (__index,
                                                            status,
                                                            song_title,
                                                            song_link,
                                                            artist,
                                                            artist_playlists[artist],))
                print("###### Write '{}' in Excel ######\n".format(status))
                __index += 1
        # make header auto filter
        artist_worksheet.autofilter(0, 0, _row_number, 5)
        try:
            artist_worksheet.write(_row_number+2, 0, "COUNT:")
            artist_worksheet.write_formula(_row_number+2, 1, '=COUNTBLANK(B2:B{})'.format(_row_number+1))
        except Exception as e:
            print(e)
            pass
        worksheet_cells[_search_name] = [(_row_number+2, 1)]
        print("|||||| Next Worksheet |||||||")
    query = workbook.q_to_sum_cells_across_worksheets(worksheet_cells)
    print("CALCULATING TOTAL COUNT: {}".format(query))
    workbook.write_in_summary(summary)  # write count to summary page
    print("==== SUMMARY CREATED ====")
    workbook.close()
    print("||||||||||||||||| WORKBOOK CLOSE: {}.xlsx |||||||||||||||||\n".format(genre))


def youtube_playlist_search(data, primary, genre):
    """
    search for playlist in YouTube and get songs in the playlist without duplication
    :param data: txt file containing artists in the same genre
    :param primary: primary genre for folder creation
    :param genre: genre that the list of artists belong to
    :return: None
    """
    __browser = chrome_driver_setup()
    artists = txt_to_list(data, delimiter=',')
    make_directory("results")
    make_directory("results/{}".format(primary))
    workbook_path = "results/{}/{}".format(primary, genre)
    workbook = XlsxWorkbook(workbook_path)
    print(" ============== NEW WORKBOOK: {}.xlsx =============\n".format(genre))
    summary = workbook.create_summary()  # create a summary page
    worksheet_cells = dict()
    for artist in artists:
        __non_artist_count = 0
        print("------------------- Writing Worksheet: {} -------------------".format(artist))
        if len(artist) > 25:
            _worksheet_name = artist[:20] + "..."
        else:
            _worksheet_name = artist
        _search_name = _worksheet_name.replace("'", "''")
        artist_worksheet = workbook.create_worksheet(_worksheet_name)
        if artist_worksheet is None:
            print("|||||| Failed to create worksheet ||||||")
            continue
        artist_worksheet.set_column('A:A', 6)
        artist_worksheet.set_column('B:B', 18)
        artist_worksheet.set_column('C:C', 70)
        artist_worksheet.set_column('D:D', 100)
        artist_worksheet.set_column('E:E', 15)
        artist_worksheet.set_column('F:F', 100)
        artist_worksheet.write_row('A1', c.HEADER)
        _row_number = 0
        search_string = f"\"{artist}\" top tracks, playlist"
        query = query_generator(search_string)
        __browser.get("https://www.youtube.com/results?search_query={}".format(query))
        try:
            playlist_url_section = __browser.find_elements_by_xpath('//yt-formatted-string[@id="view-more"]')[0]
        except Exception:
            print("NO PLAYLIST FOUND!")
            continue
        playlist_url = playlist_url_section.find_element_by_tag_name('a').get_attribute('href')
        __browser.get(playlist_url)
        scroll_down(__browser, c.SCROLL_PAGE)
        contents = __browser.find_element_by_xpath('//div[@id="contents"]')
        song_lists = contents.find_elements_by_xpath('//a[@class="yt-simple-endpoint style-scope ytd-playlist-video-renderer"]')
        __index = 1
        make_directory("src/memo/{}".format(genre))
        print("FOUND {} SONGS".format(len(song_lists)))
        for song in song_lists:
            _row_number += 1
            song_link = song.get_attribute('href')

            if link_validate(song_link, "playlist"):
                song_title = song.find_element_by_id('video-title').get_attribute('title')
                try:
                    song_thumb = song.find_element_by_id('byline').find_element_by_tag_name('a').text.lower()
                except Exception:
                    song_thumb = ""
                check, score = duplicate_validate(song_title+"\n", "src/memo/{}/memo_{}.txt".format(genre, artist))
                print("++++++ Validating song: {} ++++++".format(song_title))
                input_sentence = song_title.lower() + " " + song_thumb
                j_converted = convert_japanese(input_sentence)
                uniconverted = unidecode(j_converted)
                playlist_search_logger.debug(artist.lower() + "|" + uniconverted)
                if check:
                    playlist_search_logger.warn("DUPLICATE FOUND IN THE MEMO. REJECTED: {}".format(song_title))
                    status = "DUPLICATE {}".format(score)
                elif is_intitle("live", song_title.lower()):
                    playlist_search_logger.warn("LIVE PERFORMANCE. REJECTED: {}".format(song_title))
                    status = "LIVE PERFORMANCE"
                elif is_intitle("remix", song_title.lower()):
                    playlist_search_logger.warn("REMIX. REJECTED: {}".format(song_title))
                    status = "REMIX"
                elif is_intitle("cover", song_title.lower()):
                    playlist_search_logger.warn("SONG COVER. REJECTED: {}".format(song_title))
                    status = "COVER"
                elif not is_best_match(artist.lower(), uniconverted):
                    playlist_search_logger.warn("SONG TITLE DOES NOT CONTAIN ARTIST NAME. REJECTED: {}".format(song_title))
                    status = "NOT FROM ARTIST"
                    __non_artist_count += 1
                else:
                    status = ""
                    memo_generator(song_title+"\n", "src/memo/{}/memo_{}.txt".format(genre, artist))
                artist_worksheet.write_row(_row_number, 0, (__index,
                                                            status,
                                                            song_title,
                                                            song_link,
                                                            artist,
                                                            playlist_url))
                print("###### Write '{}' in Excel ######\n".format(status))
                __index += 1
        # make header auto filter
        artist_worksheet.autofilter(0, 0, _row_number, 5)
        try:
            artist_worksheet.write(_row_number+2, 0, "COUNT:")
            artist_worksheet.write_formula(_row_number+2, 1, '=COUNTBLANK(B2:B{})'.format(_row_number+1))
        except Exception as e:
            print(e)
            pass
        worksheet_cells[_search_name] = [(_row_number+2, 1)]

        # check if non artists labels too many -- might be wrong search
        if __non_artist_count > _row_number*0.5 or _row_number <= 10:
            d = {
                "artist": artist,
                "error count": __non_artist_count,
                "percentage error": round(__non_artist_count * 100 / _row_number, 2),
                "playlist url": playlist_url,
                "total number": _row_number,
                "correction": ""
            }
            path = "src/memo/{}_error.json".format(genre)
            if not os.path.exists(path):
                print("error memo path does not exist!")
                json_writer_overwrite(d, path)
            else:
                print("error memo exists, append to error memo")
                json_writer_append(d, path)

        print("|||||| Next Worksheet |||||||")
    query = workbook.q_to_sum_cells_across_worksheets(worksheet_cells)
    print("CALCULATING TOTAL COUNT: {}".format(query))
    workbook.write_in_summary(summary)  # write count to summary page
    print("==== SUMMARY CREATED ====")
    workbook.close()
    print("||||||||||||||||| WORKBOOK CLOSE: {}.xlsx |||||||||||||||||\n".format(genre))
