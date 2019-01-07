#!/usr/bin/env python3
# vim: set et ts=4 sw=4 sts=4:

import os
import shutil

NAS_ROOT = '/volume1/music'
BENDER_ROOT = '/media/nastynas/music'
ROOT = '/home/bart/Music'
ALBUM_DIRNAME_FORMAT = '{album_artist} - {year} - {album}'

def func_apply(val, *funcs):
    if not funcs:
        return val
    return func_apply(funcs[0](val), *funcs[1:])

def escape_chars(path, to_escape_chars, subst_char='_'):
    return path.translate(
        str.maketrans(to_escape_chars, len(to_escape_chars)*subst_char)
    )

def decode_path_part(path_part):
    if type(path_part) == bytes:
        return path_part.decode('utf8')
    return path_part

def sanitize_path_part(path_part):
    path_part = decode_path_part(path_part)
    _ = '_'

    escape_funcs = [
        lambda p: escape_chars(p, '\\/', _),              # Slashes.
        lambda p: _+p[1:] if p[0]=='.' else p,            # Leading dot.
        lambda p: p.translate(dict.fromkeys(range(32))),  # Control chars.
        lambda p: escape_chars(p, '<>:"?*|', _)           # Windows reserved.
    ]
    sane_path_part = func_apply(path_part, *escape_funcs)

    return sane_path_part

def mkdir(path):
            try:
                os.mkdir(path)
            except FileExistsError:
                pass

def symlink(src, dest):
    try:
        os.symlink(src, dest)
    except FileExistsError:
        pass

def renew_album_symlinks(old_dirs, new_albums, genres):
    for album_dir in [dir_ for dir_ in old_dirs
                           if dir_.startswith(ROOT)]:
        shutil.rmtree(album_dir)

    for album_path, props in new_albums.items():
        if not genres:
            genres = ['__No genre']
        for genre in genres:
            genre_dirname = sanitize_path_part(genre)
            genre_dirpath = os.path.join(ROOT, genre_dirname)
            mkdir(genre_dirpath)
        album_dirname = sanitize_path_part(ALBUM_DIRNAME_FORMAT.format(album_artist=props['album_artist'], year=props['year'], album=props['album']))
        album_dirpath = os.path.join(genre_dirpath, album_dirname)
        mkdir(album_dirpath)

        rebased_album_path = os.path.join(BENDER_ROOT, album_path.split(NAS_ROOT)[1].strip(os.sep))
        for item in os.listdir(rebased_album_path):
            symlink(os.path.join(rebased_album_path, item),
                    os.path.join(album_dirpath, item))
