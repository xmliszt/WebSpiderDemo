## This is a demo. Sensitive data and private information are removed.
---
## Complex Search Flow
```plain
>>> process raw data
>>> store in json for backup and next-time usage (query)
>>> make a copy of backup for usage
>>> send request
>>> get primary response
>>> process/convert response for next input
>>> send request
>>> get secondary response
...
>>> get final response
>>> process/convert response
>>> extract necessary information from response
>>> update copy of query
>>> youtube search for query items
>>> process search results and filter them
>>> output results in local file (csv)
```
---
## Playlist Search Flow
```plain
>>> process raw txt data to get list of artists
>>> pass each artist into YouTube playlist search directly
>>> go into the playlist page
>>> obtain song title and song url
>>> check for duplication, prefer keeping the one containing "official" keyword
>>> output song titles and url
```
---
## General Utilities
_Detailed usage of the utilities please see_ `general_utils.py`<br/>
<br/>
`txt_to_list(file, delimiter)`<br/>
`csv_writer_overwrite(path, *args)`<br/>
`csv_writer_append(path, *args)`<br/>
`json_to_dict(j, local=True)`<br/>
`json_writer_overwrite(d, path)`<br/>
`json_writer_append(d, path)`<br/>
`html_generator(url)`<br/>
`request_sender(url, **kwargs)`<br/>
`metatdata_search(link, *args)`<br/>
`query_generator(search_string)`<br/>
`fuzzy_validate(target, base)`<br/>
`keyword_validate(target, keywords)`<br/>
`memo_generator(entry, output_path)`<br/>
`memo_validate(target, memo_path)`<br/>
`duplicate_validate(target, memo_path)`<br/>
`chunk(lst, n)`<br/>
---