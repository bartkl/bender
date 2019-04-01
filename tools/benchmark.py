#!/usr/bin/env python3
# vim: set et ts=4 sw=4 sts=4:

import sys
import os
import subprocess
import sqlite3
import time

CONFIG = {
    'beets db': '/media/nastynas/homes/bart/.config/beets/library.db',
    'genre delimiter': ',',
}

def fetch_all(conn):
    albums = {}

    c = conn.cursor()
    c.execute('''
        select
            albums.id,
            albums.genre,
            albums.year,
            albums.albumartist,
            albums.album,
            items.path
        from albums

        inner join items
        on albums.id = items.album_id

        group by album_id
        ''')

    for id_, genres, year, album_artist, album, path in c:
        path = path.decode('utf8')
        album_path = os.path.dirname(path)
        albums[album_path] = {
            'id': id_,
            'genres': genres.split(CONFIG['genre delimiter']),
            'year': year,
            'album_artist': album_artist,
            'album': album,
        }
    return albums

def fetch_ten(conn):
    albums = {}
    paths = (
        b'/volume1/music/Aphex Twin - 2014 - Syro/04 - 4 bit 9d api+e+6.mp3',
        b'/volume1/music/Duran Duran - 1982 - Rio/01 - Rio.mp3',
        b'/volume1/music/Emerson, Lake & Palmer - 1970 - Emerson, Lake & Palmer/01 - The barbarian.mp3',
        b'/volume1/music/Frank Zappa - 1970 - Weasels Ripped My Flesh/03 - Prelude to the afternoon of a sexually aroused gas mask.flac',
        b'/volume1/music/Todd Terje - 2013 - Strandbar/03 - Strandbar (bonus version).mp3',
        b'/volume1/music/Le Orme - 1971 - Collage/04 - Sguardo verso il cielo.mp3',
        b'/volume1/music/Deerhunter - 2008 - Microcastle/08 - Activa.mp3',
        b'/volume1/music/Ludwig van Beethoven - 1974 - Symphonies Nos. 5 & 7 (Carlos Kleiber & Wiener Philharmoniker)/03 - Symphony no. 5 in C minor, op. 67 - III. Allegro.mp3',
        b'/volume1/music/Clams Casino - 2012 - Instrumental Mixtape 2/06 - One last thing.mp3',
        b"/volume1/music/Curtis Mayfield - 1970 - Curtis/01 - (Don't worry) if there's a hell below we're all going to go.mp3"
    )

    c = conn.cursor()
    c.execute('''
        select
            albums.id,
            albums.genre,
            albums.year,
            albums.albumartist,
            albums.album,
            items.path
        from albums

        inner join items
        on albums.id = items.album_id

        where path in (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        group by album_id
        ''', paths)

    for id_, genres, year, album_artist, album, path in c:
        path = path.decode('utf8')
        album_path = os.path.dirname(path)
        albums[album_path] = {
            'id': id_,
            'genres': genres.split(CONFIG['genre delimiter']),
            'year': year,
            'album_artist': album_artist,
            'album': album,
        }
    return albums

if __name__ == '__main__':
    conn = sqlite3.connect(CONFIG['beets db'])
    fetch_all_starttime = time.time()
    fetch_all(conn)
    fetch_all_endtime = time.time()
    print("Time for all albums was {}".format(fetch_all_endtime - fetch_all_starttime))

    fetch_ten_starttime = time.time()
    fetch_ten(conn)
    fetch_ten_endtime = time.time()
    print("Time for ten albums was {}".format(fetch_ten_endtime - fetch_ten_starttime))
