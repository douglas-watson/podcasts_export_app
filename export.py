#!/usr/bin/env python3
#
#  Podcasts Export
#  ---------------
#  Douglas Watson, 2022, MIT License
#
#  export.py: reads list of available episodes from to Podcasts.app database, 
#             copies downloaded episodes to specified folder.

import os
import sys
import shutil
import urllib.parse
import sqlite3
import datetime

from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.easyid3 import EasyID3


SQL = """
SELECT p.ZAUTHOR, p.ZTITLE, e.ZTITLE, e.ZASSETURL, e.ZPUBDATE
from ZMTEPISODE e 
join ZMTPODCAST p
    on e.ZPODCASTUUID = p.ZUUID 
where ZASSETURL NOTNULL;
"""


def get_downloaded_episodes(set_progress):
    """ Returns list of episodes.
    Format [[author, podcast, title, path, zpubdate], ...]
    """
    return sqlite3.connect(get_db_path()).execute(SQL).fetchall()
    
def get_db_path():
    return os.path.expanduser(
        "~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Documents/MTLibrary.sqlite")

def export(episodes, output_dir, set_progress=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    counter = 0
    for author, podcast, title, path, zpubdate in episodes:
        if set_progress is not None:
            set_progress(int(counter / len(episodes) * 100))
        counter += 1

        safe_title = title.replace('/', '|').replace(':', ',')
        safe_podcast = podcast.replace('/', '|').replace(':', ',')
        safe_author = author.replace('/', '|').replace(':', ',')
        pubdate = datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=zpubdate)

        podcast_path = os.path.join(output_dir, safe_podcast)
        if not os.path.exists(podcast_path):
            os.makedirs(podcast_path)

        dest_path = os.path.join(podcast_path,
                                 u"{:%Y.%m.%d}-{}-({}).mp3".format(pubdate, safe_title[0:140], safe_author[0:100]))
        try:
            shutil.copy(urllib.parse.unquote(path[len('file://'):]), dest_path)
        except IsADirectoryError:
            print(u"Failed to export {} - {}, media file is not an mp3 file".format(podcast, title))
            continue

        try:
            mp3 = MP3(dest_path, ID3=EasyID3)
        except HeaderNotFoundError:
            print(u"Corrupted file: {} - {}".format(podcast, title))
            continue
        if mp3.tags is None:
            mp3.add_tags()
        mp3.tags['artist'] = author
        mp3.tags['album'] = podcast
        mp3.tags['title'] = title
        mp3.save()
