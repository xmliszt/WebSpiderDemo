# ARTIST-SONGS EXTRACTION #

MAX_ALBUM_NUMBER = 30

SPOTIFY_CLIENTID = '' # Your Spotify Client ID
SPOTIFY_SECRET = '' # Your Spotify App Secret

DISCORG_TOKEN = "" # Your Discorg token
DISCORG_API = "https://api.discogs.com/"

# YOUTUBE SEARCH #

SCROLL_PAGE = 4

DURATION_TOLERANCE = 10
MAX_DURATION_TOLERANCE = 20

TITLE_MATCH_THRESHOLD = 40
INTITLE_THRESHOLD = 80  # for danger keyword checking in title
DUPLICATE_THRESHOLD = 98  # for checking if pick duplicate songs
FUZZ_THRESHOLD = 80  # for checking if match query
KEYWORD_THRESHOLD = 0.9

DANGER_WORDS = ['compilation']  # words do not want in the title

YOUTUBE_URL = "https://www.youtube.com/results"
YOUTUBE = "https://www.youtube.com"

# EXCEL WRITER #

HEADER = (
        "Index",
        "Status",
        "Song Title",
        "YouTube Link",
        "Artist",
        "Playlist Link"
)

# MISCELLANEOUS #

YDL_OPTS = {                                            # parameters for metadata extraction
        'format': 'bestaudio/best',
        'outtmpl': 'tmp/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'prefer_ffmpeg': True,
        'audioformat': 'wav',
        'forceduration': True
    }

CHROMEDRIVER_PATH = ''  # Your Chrome Driver path
