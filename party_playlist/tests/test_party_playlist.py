import sys
import _thread as thread
import queue
import time
import pytest
from contextlib import suppress
import os
import pdb

from party_playlist import PartyPlaylist, Party, GENERAL_CFG_FILE
import contribution
import collection
import db_utils
import func

TEST_COLLECTION = 'test_collection_XD'
TEST_CONTRIBUTION = 'test_contribution_XD'
if os.path.isdir('songs'):
    SONG_FOLDER = os.path.join(os.getcwd(), 'songs')
else:
    SONG_FOLDER = os.path.join(os.getcwd(), 'tests', 'songs')

class PartyPlaylistForTesting(PartyPlaylist):
    def __init__(self, **party_args):
        PartyPlaylist.__init__(self)
        self.create_cfg(GENERAL_CFG_FILE)
        self.setup_paths()
        self.party_args = party_args

    def start(self):
        Party(TEST_COLLECTION, **self.party_args)

@pytest.mark.a
def test_get_us_a_collections_creates_new_collection():
    '''testing the underlying function'''
    # making sure was cleaned up properly
    party = PartyPlaylistForTesting()
    with suppress(Exception):
        here = os.path.join(party.path_collections, TEST_COLLECTION+'.db')
        os.remove(here)
        # collection.delete_collection(TEST_COLLECTION)

    for collection in func.get_collections(app=party):
        name = func.get_collection_name(collection)
        if name == TEST_COLLECTION:
            raise Exception("Deleteing playlist failed...")

    collection.setup(TEST_COLLECTION, create=True, test=False)
    name = func.get_collection_name(TEST_COLLECTION)
    assert name == TEST_COLLECTION
    for collection in func.get_collections(app=party):
        pdb.set_trace()
        name = func.get_collection_name(collection)
        if name == TEST_COLLECTION:
            with suppress(Exception):
                delete_collection(TEST_COLLECTION)
            break
    else:
        raise Exception('The new command failed to create a new playlist...')


def test_new_command_creates_new_playlist():
    '''testing the command as if it was input from commandline'''
    with suppress(Exception):
        collection.delete_collection(TEST_COLLECTION)
    thread.start_new_thread(Party,(), {'name':TEST_COLLECTION, 'load':False})
    # give it time to create and what not
    time.sleep(1)
    for playlist in PlaylistInfo.select():
        if playlist.name == TEST_COLLECTION:
            break
    else:
        raise Exception('The new command failed to create a new playlist...')

@pytest.mark.t
def test_delete_command_deletes_playlist():
    '''testing the command as if it was input from commandline'''
    with suppress(Exception):
        collection.delete_collection(TEST_COLLECTION)
    thread.start_new_thread(Party,(), {'name':TEST_COLLECTION, 'load':False})
    # give it time to create and what not
    time.sleep(1)
    for playlist in PlaylistInfo.select():
        if playlist.name == TEST_COLLECTION:
            break
    else:
        raise Exception('The new command failed to create a new playlist...')


def test_finder_linux():
    '''we test that we can add/remove paths from the finder and that a song gets found and added to the database
    correctly'''
    if os.name == 'nt':
        return
    party = PartyPlaylistForTesting(stdin=False)
    try:
        finder = contribution.FindMusic(app=party, device='pc', db_name=TEST_CONTRIBUTION, paths=(SONG_FOLDER,), default_paths=False)

        db = db_utils.connect_db(db_utils.UserContribution, finder.db_path)
        song  = db_utils.UserContribution.get(db_utils.UserContribution.title=='test')
        import pdb;pdb.set_trace()

        assert song.title == 'test_title'
        assert song.album == 'test_album'
        assert song.artist == 'test_artist'
        assert song.genre == 'test_genre'
    finally:
        collection.delete_collection()
        os.remove(finder.db_path)

def test_picking_up_pushed_collection():
    party = Party(stdin=False)



def test_tracks_on_queue_get_made_into_playlist():
    # Doesn't block input
    party = Party(stdin=False)
    party.track_queue.put()
    pass

def test_music_source_youtube():
    pass

def test_songs_get_found_from_nfc():
    pass

def test_songs_get_found_from_wifi():
    pass
