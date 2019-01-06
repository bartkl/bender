#!/usr/bin/env python3
# vim: set et ts=4 sw=4 sts=4:

import os
from config import Config


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
        return path_part.decode(Config['path encoding'])
    return path_part

def sanitize_path_part(path_part):
    path_part = decode_path_part(path_part)
    _ = Config['subst char']

    escape_funcs = [
        lambda p: escape_chars(p, '\\/', _),              # Slashes.
        lambda p: _+p[1:] if p[0]=='.' else p,            # Leading dot.
        lambda p: p.translate(dict.fromkeys(range(32))),  # Control chars.
        lambda p: escape_chars(p, '<>:"?*|', _)           # Windows reserved.
    ]
    sane_path_part = func_apply(path_part, *escape_funcs)

    return sane_path_part

def rebase_library(path, target_root):
    match_found = False
    for src_root in Config['library root'].values():
        path_parts = path.split(src_root)
        if len(path_parts) > 1:
            match_found = True
            break
    if match_found:
        return os.path.join(Config['library root'][target_root],
                            path_parts[1].lstrip(os.sep))
    else:
        raise Exception('No source found.')

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
