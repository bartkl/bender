#!/usr/bin/env python3
# vim: set et ts=4 sw=4 sts=4:

import sqlite3
from config import Config
import utils


def fetch_album(conn, path_base=None):
    c = conn.cursor()
    c.execute('''
        select
            items.path,
            albums.albumartist,
            albums.year,
            albums.album,
            albums.genre
        from items

        inner join albums
        on items.album_id = albums.id

        group by items.id
    ''')
    while True:
        album = c.fetchone()
        if album is None:
            return

        path = utils.decode_path_part(album[0])
        if path_base:
            path = utils.rebase_library(path, path_base)
        album_artist = album[1]
        year = album[2]
        album_title = album[3]
        genres = album[4].split(Config['genre separator'])

        yield (path, album_artist, year, album_title, genres)
