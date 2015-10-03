import sys
import _thread as thread
import queue
import time

from party_playlist import Party
# from party_playlist.db_utils import PlaylistInfo
from db_utils import PlaylistInfo


def test_new_command_creates_new_playlist():
    thread.start_new_thread(Party,(), {'name':'test_playlist_XD', 'load':False})
    # give it time to create and what not
    time.sleep(90)
    for playlist in PlaylistInfo.select():
        if playlist.name == 'test_playlist_XD':
            break
    else:
        # import pdb; pdb.set_trace()
        raise Exception('The new command failed to create a new playlist...')
