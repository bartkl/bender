#!/usr/bin/env python3
import os
import gzip
import shutil
from pprint import pprint

TAG_CACHE_FILEPATH = '/home/bart/tag_cache.gz'

class TagCacheApi():

    def __init__(self, tag_cache_filename=TAG_CACHE_FILEPATH):
        self._tag_cache_file = gzip.open(tag_cache_filename, 'rt+')
        self._previous_line_position = None


    """ Properties and setters. """
    @property
    def previous_line_position(self):
        return self._previous_line_position

    @previous_line_position.setter
    def previous_line_position(self, position):
        self._previous_line_position = position

    @property
    def tag_cache_file(self):
        return self._tag_cache_file

    def read_line_and_store_position(self):
        self.previous_line_position = self.tag_cache_file.tell()
        return self.tag_cache_file.readline()

    def seek_to_line(self, match_text, stop_at_text=None, compare_func=None):
        tag_cache_file = self.tag_cache_file

        if compare_func is None:
            def compare_func(line, match_text):
                if line == match_text+'\n':
                    return True
                else:
                    return False

        while True:
            line = self.read_line_and_store_position()
            if compare_func(line, match_text):
                return tag_cache_file
            elif line == '%s\n' % stop_at_text or line == '':
                break

        raise LineNotFoundError(match_text, stop_at_text, compare_func)


    def seek_to_song(self, song, directory=None):
        tag_cache_file = self.tag_cache_file

        """ If `directory' is passed, seek to it. """
        if directory is not None:
            self.seek_to_directory(directory)

        songFound = self.seek_to_line('song_begin: %s' % song, 'end: %s' % directory)
        if songFound:
            return tag_cache_file

        return False

    def seek_to_directory(self, directory):
        tag_cache_file = self.tag_cache_file

        directoryFound = self.seek_to_line('directory: %s' % directory)
        if directoryFound:
            return tag_cache_file

        return False


    def get_current_line(self):
        self.tag_cache_file.seek(self.previous_line_position)
        return self.read_line_and_store_position()

    def get_song(self, file_path, seek_to_directory=True, reset_position_afterwards=True):
        directory, song = self.get_song_and_directory_from_path(file_path)

        if seek_to_directory:
            try:
                self.seek_to_song(song, directory)
            except LineNotFoundError as e:
                raise SongNotFoundError(file_path, line_not_found_exception=e)

        song_metadata = {}
        line = self.read_line_and_store_position()
        while line != 'song_end\n':
            line_parts = line.split(':')
            key = line_parts[0].strip()
            value = line_parts[1].strip()

            if key in song_metadata.keys():
                if type(song_metadata[key]) == 'list':
                    song_metadata[key].append(value)
                else:
                    song_metadata[key] = [song_metadata[key], value]
            else:
                song_metadata[key] = value

            line = self.read_line_and_store_position()

        if reset_position_afterwards:
            self.tag_cache_file.seek(0)
        return song_metadata
        # Filepath info doesn't need to be included.

    def get_field(self, song, field): # Or remove this?
        pass

    def get_directory(self, file_path, reset_position_afterwards=True):
        directory = file_path.rstrip('/')

        try:
            self.seek_to_directory(directory)
        except LineNotFoundError as e:
            raise DirectoryNotFoundError(file_path, line_not_found_exception=e)

        directory_metadata = {}
        line = self.read_line_and_store_position()
        while line != 'end: %s\n' % directory:
            if line.startswith('song_begin: '):
                song = line.split('song_begin: ')[1].rstrip('\n')
                song_metadata = self.get_song(song, seek_to_directory=False, reset_position_afterwards=False)
                directory_metadata[song] = song_metadata

            line = self.read_line_and_store_position()

        if reset_position_afterwards:
            self.tag_cache_file.seek(0)
        return directory_metadata

    def get_song_and_directory_from_path(self, file_path):
        return os.path.dirname(file_path), os.path.basename(file_path)

    def update_song(self, file_path, metadata):
        # Store current song block in object form.
        try:
            song_metadata_current = self.get_song(file_path)
        except SongNotFoundError as e:
            print(e)
            return False

        # Seek to song.
        directory, song = self.get_song_and_directory_from_path(file_path)
        try:
            self.seek_to_song(song, directory)
        except LineNotFoundError as e:
            # Consider: save position before try block and rewind to that position here?
            raise SongNotFoundError(file_path, line_not_found_exception=e)
        song_block_begin_position = self.previous_line_position

        # Write all lines previous to the song block to temp file.
        self.tag_cache_file.seek(0)
        with gzip.open(TAG_CACHE_FILEPATH+".tmp.gz", 'wt') as t:
            while self.tag_cache_file.tell() <= song_block_begin_position:
                line = self.read_line_and_store_position()
                t.write(line)

        # Write the new song_block contents.
            for field in song_metadata_current.keys():
                if field in metadata.keys():
                    print("Using new")
                    value = metadata[field]
                else:
                    print("Using original")
                    value = song_metadata_current[field]

                if type(value) == list:
                    for element in list:
                        t.write("%s: %s\n" % (field, element))
                else:
                    t.write("%s: %s\n" % (field, value))

        # Write the rest of the original file.
            try:
                self.seek_to_line("song_end")
            except LineNotFoundError as e:
                print(e)
            
            line = self.read_line_and_store_position()
            while line != '':
                t.write(line)
                line = self.read_line_and_store_position()

        # Replace the original file with the new, temporary file.
        self.tag_cache_file.close()
        shutil.move(TAG_CACHE_FILEPATH+".tmp.gz", TAG_CACHE_FILEPATH)



def main():
    tag_cache_api = TagCacheApi()
    test_directory = "Pink Floyd - 1979 - The Wall"
    test_song = "26 - Outside the wall.mp3"

    #tag_cache_api.seek_to_directory(test_directory)
    #tag_cache_api.seek_to_line('rectory:', compare_func=cmp)
    #tag_cache_api.seek_to_song(test_song)
    #tag_cache_api.seek_to_song(test_song, directory=test_directory)
    #tag_cache_api.get_song(test_directory+'/'+test_song)
    # try:
    #     pprint(tag_cache_api.get_directory(test_directory))
    # except DirectoryNotFoundError as e:
    #     print(e)
    try:
        pprint(tag_cache_api.get_song(test_directory+'/'+test_song))
    except SongNotFoundError as e:
        print(e)
    tag_cache_api.update_song(test_directory+"/"+test_song, {'Album': 'THEWLL', 'Genre': 'Art Rock'})
    #tag_cache_api.tag_cache_file.seek(tag_cache_api.previous_line_position)
    #pprint(tag_cache_api.get_current_line())

""" Exceptions """
class Error(Exception):
    pass

class LineNotFoundError(Error):
    def __init__(self, match_text, stop_at_text, compare_func):
        self.message = "No line was found to match text:\n%s\nusing compare function:\n%s\nand stop_at_text:\n%s" % (match_text, compare_func, stop_at_text)

    def __str__(self):
        return self.message

class SongNotFoundError(Error):
    def __init__(self, file_path, line_not_found_exception=None):
        self.message = "The song %s was not found.\n" % file_path
        if line_not_found_exception:
            self.message += "The preceding, underlying line not found exception information: %s" % line_not_found_exception

    def __str__(self):
        return self.message

class DirectoryNotFoundError(Error):
    def __init__(self, file_path, line_not_found_exception=None):
        self.message = "The directory %s was not found.\n" % file_path
        if line_not_found_exception:
            self.message += "The preceding, underlying line not found exception information: %s" % line_not_found_exception

    def __str__(self):
        return self.message


if __name__ == '__main__':
    main()






""" Notes:
    - There is no `update_directory()' method, since there is no
      metadata other than `mtime', which one would never want to
      update.
    - No methods for the actions of creation and deletion are
      implemented. Issuing an `update' command to MPD takes good
      care of this natively.
    - All seek function other than the primal `seek_to_line' don't
    have `compare_func' arguments, since this beats their conceptual
    purpose of seeking by identifier.
    - Endpoints are supposed to be stateless, so no
    `get_song_in_directory' function should exist, since 'current'
    implies state.
"""





