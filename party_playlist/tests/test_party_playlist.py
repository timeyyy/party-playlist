import _thread as thread
import time
import pytest
from contextlib import suppress
import os
import pdb
import json

import peewee

from party_playlist import PartyPlaylist, Party, GENERAL_CFG_FILE
from party_playlist import db_utils, contribution_func, collection_func, process_tracks, func

# import contribution_func
# from db_utils import *
# import db_utils
# import collection_func
TEST_COLLECTION = 'test_collection_XD'
TEST_CONTRIBUTION = 'test_contribution_XD'
TEST_USER = 'test_user'
TEST_USER2 = TEST_USER+'2'
TEST_CONTRIBUTION2 = TEST_CONTRIBUTION+'2'

if os.path.isdir('songs'):
    SONG_FOLDER = os.path.join(os.getcwd(), 'songs')
else:
    SONG_FOLDER = os.path.join(os.getcwd(), 'tests', 'songs')

def setup_function(func):
    party = PartyPlaylistForTesting()
    with suppress(FileNotFoundError):
        collection_func.delete_collection(party.path_collection, TEST_COLLECTION)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_my_contribution, TEST_CONTRIBUTION)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_other_contribution, TEST_CONTRIBUTION)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_my_contribution, TEST_CONTRIBUTION2)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_other_contribution, TEST_CONTRIBUTION2)

def teardown_function(func):
    party = PartyPlaylistForTesting()
    with suppress(FileNotFoundError):
        collection_func.delete_collection(party.path_collection, TEST_COLLECTION)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_my_contribution, TEST_CONTRIBUTION)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_other_contribution, TEST_CONTRIBUTION)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_my_contribution, TEST_CONTRIBUTION2)
    with suppress(FileNotFoundError):
        contribution_func.delete_contribution(party.path_other_contribution, TEST_CONTRIBUTION2)


class MockFinder(contribution_func.FindMusic):
    def __init__(self, user, **kwargs):
        self.user = user
        contribution_func.FindMusic.__init__(self, **kwargs)

    def get_unique_name(self):
        return self.user

class PartyPlaylistForTesting(PartyPlaylist):
    # Todo, need to make this even more mocklike!, failures in threads shouldnt fuck up my stuff..

    class PartyMock(Party):
        def __init__(self, app):
            if 'find_new_tracks' in app.mask_out:
                def find_new_tracks(*args, **kwargs):
                    pass
                self.find_new_tracks = find_new_tracks
            if 'playlist_from_tracks' in app.mask_out:
                def playlist_from_tracks(*args, **kwargs):
                    pass
                self.playlist_from_tracks = playlist_from_tracks
            if 'process_tracks' in app.mask_out:
                def process_tracks(*args, **kwargs):
                    pass
                self.process_tracks = process_tracks

            Party.__init__(self, app=app, name=TEST_COLLECTION, **app.party_args)

    def __init__(self,*mask_out, **party_args):
        '''pass in non keyword args, the functions will be subclassed and just pass, aka not cause false errors,
        party args are arguments for the Party class'''
        PartyPlaylist.__init__(self)
        self.create_cfg(GENERAL_CFG_FILE)
        self.setup_paths()
        self.party_args = party_args
        self.mask_out = mask_out

    def start(self):
        self.party = self.PartyMock(app=self)
        with db_utils.LOCK:
            time.sleep(5)


def test_create_or_get_collection():
    '''testing the underlying function for creating a new collection, also deleteing'''
    # making sure was cleaned up properly
    party = PartyPlaylistForTesting()
    our_file = os.path.join(party.path_collection, TEST_COLLECTION + '.db')
    assert not os.path.exists(our_file)

    collection_func.create_or_get_collection(party.path_collection,
                                             TEST_COLLECTION,
                                             load=False)
    assert os.path.exists(our_file)

    collection_info = collection_func.create_or_get_collection(party.path_collection,
                                                               TEST_COLLECTION,
                                                               load=True)
    assert collection_info.name == TEST_COLLECTION

    for collection in collection_func.get_collections(party.path_collection):
        if collection == TEST_COLLECTION:
            collection_func.delete_collection(party.path_collection, TEST_COLLECTION)
            assert not os.path.exists(our_file)
            break
    else:
        raise Exception('The new command failed to create a new playlist...')


def test_new_command_creates_new_collection():
    '''testing the command as if it was input from commandline'''
    party = PartyPlaylistForTesting('find_new_tracks', 'process_tracks', stdin=False)
    party.start()
    for collection in collection_func.get_collections(party.path_collection):
        if collection == TEST_COLLECTION:
            break
    else:
        raise Exception('The new command failed to create a new collection...')

#TODO incomplete
@pytest.mark.xfail
def test_delete_command_deletes_playlist():
    '''testing the command as if it was input from commandline'''
    party = PartyPlaylistForTesting(stdin=False)
    for collection in collection_func.get_collections(party.path_collection):
        if collection == TEST_COLLECTION:
            break
    else:
        raise Exception('The new command failed to create a new playlist...')


def test_finder_folders():
    '''we test that we can add/remove paths from the finder and that a song gets found and added to the database
    correctly'''
    party = PartyPlaylistForTesting(stdin=False)
    finder = MockFinder(TEST_USER, app=party, device='pc', db_name=TEST_CONTRIBUTION)
    finder.folders(paths=[SONG_FOLDER], default_paths=False)

    with db_utils.connected_db(db_utils.UserContribution, finder.path):
        song  = db_utils.UserContribution.get(db_utils.UserContribution.title=='test_title')
        assert song.title == 'test_title'
        assert song.album == 'test_album'
        assert song.artist == 'test_artist'
        assert song.genre == 'test_genre'



def test_pushing_contribution_to_collection_and_also_getting_contribution():
    '''we mute out all the detection and queue effects, we test pushing, and getting and the effects that they should have'''
    # make our new collection
    party = PartyPlaylistForTesting('find_new_tracks', 'process_tracks', stdin=False)
    party.start()

    # make our contribution
    finder = MockFinder(TEST_USER, app=party, device='pc', db_name=TEST_CONTRIBUTION)
    finder.folders(paths=[SONG_FOLDER], default_paths=False)


    # test get new contrib fails silently when nothing to return
    new_contribution = contribution_func.get_new_contributions(party.path_collection, TEST_COLLECTION)
    with pytest.raises(StopIteration):
        next(new_contribution)

    # push the contribution
    contribution_func.push_contribution(party.path_my_contribution,
                                        contribution=TEST_CONTRIBUTION,
                                        output_path=party.path_other_contribution,
                                        collection_path=party.path_collection,
                                        collection=TEST_COLLECTION,
                                        push_method='test')

    # make sure the push worked properly
    with db_utils.connected_db(db_utils.CollectionInfo, os.path.join(party.path_collection, TEST_COLLECTION)):
        collection_info = db_utils.CollectionInfo.get()
        assert json.loads(collection_info.users)[0] == TEST_USER
        assert json.loads(collection_info.user_contributions)[0] == TEST_CONTRIBUTION

    new_contribution = contribution_func.get_new_contributions(party.path_collection, TEST_COLLECTION)
    assert next(new_contribution) == TEST_CONTRIBUTION

    # test pushing a second contribution works fine
    # make our contribution
    finder = MockFinder(TEST_USER2, app=party, device='pc', db_name=TEST_CONTRIBUTION2)
    finder.folders(paths=[SONG_FOLDER], default_paths=False)

    # push the contribution
    contribution_func.push_contribution(party.path_my_contribution,
                                        contribution=TEST_CONTRIBUTION2,
                                        output_path=party.path_other_contribution,
                                        collection_path=party.path_collection,
                                        collection=TEST_COLLECTION,
                                        push_method='test')

    with db_utils.connected_db(db_utils.CollectionInfo, os.path.join(party.path_collection, TEST_COLLECTION)):
        collection_info = db_utils.CollectionInfo.get()
        users = json.loads(collection_info.users)
        assert users[0] == TEST_USER
        assert users[1] == TEST_USER2
        contributions = json.loads(collection_info.user_contributions)
        assert contributions[0] == TEST_CONTRIBUTION
        assert contributions[1] == TEST_CONTRIBUTION2

#TODO make sure pushing works for multiple...

def test_process_tracks():
    party = PartyPlaylistForTesting('find_new_tracks', 'process_tracks', stdin=False)
    party.start()

    # make our contribution
    finder = MockFinder(TEST_USER, app=party, device='pc', db_name=TEST_CONTRIBUTION)
    finder.folders(paths=[SONG_FOLDER], default_paths=False)

    # push the contribution
    contribution_func.push_contribution(party.path_my_contribution,
                                        contribution=TEST_CONTRIBUTION,
                                        output_path=party.path_other_contribution,
                                        collection_path=party.path_collection,
                                        collection=TEST_COLLECTION,
                                        push_method='test')

    # run our algorythim on them
    process_tracks.process_tracks(collection_path=party.path_collection,
                        collection=TEST_COLLECTION,
                        contribution_path=party.path_other_contribution,
                        contribution=TEST_CONTRIBUTION)

    cfg = func.get_config()
    with db_utils.connected_collection(os.path.join(party.path_collection, TEST_COLLECTION)):
        song = db_utils.ScoredTrack.get(db_utils.ScoredTrack.title=='test_title')
        assert song.title == 'test_title'
        assert song.album == 'test_album'
        assert song.artist == 'test_artist'
        assert song.genre == 'test_genre'

        user = db_utils.UserData.get(db_utils.UserData.unique_name==TEST_USER)
        assert user.unique_name == TEST_USER

        our_score = json.loads(song.userscores)[TEST_USER]
        assert our_score == cfg['scoring']['hits_per_track']

        track = db_utils.Playlist.get(db_utils.Playlist.title == 'test_title')
        assert int(track.score) == cfg['scoring']['hits_per_track'] + cfg['scoring']['multiple_user']

    # Now lets push the same track from a new user
    # make our contribution
    finder = MockFinder(TEST_USER2, app=party, device='pc', db_name=TEST_CONTRIBUTION2)
    finder.folders(paths=[SONG_FOLDER], default_paths=False)

    # push the contribution
    contribution_func.push_contribution(party.path_my_contribution,
                                        contribution=TEST_CONTRIBUTION2,
                                        output_path=party.path_other_contribution,
                                        collection_path=party.path_collection,
                                        collection=TEST_COLLECTION,
                                        push_method='test')

    # run our algorythim on them
    process_tracks.process_tracks(collection_path=party.path_collection,
                                  collection=TEST_COLLECTION,
                                  contribution_path=party.path_other_contribution,
                                  contribution=TEST_CONTRIBUTION2)

    with db_utils.connected_collection(os.path.join(party.path_collection, TEST_COLLECTION)):
        userdata = db_utils.UserData.get(db_utils.UserData.unique_name==TEST_USER)
        userdata2 = db_utils.UserData.get(db_utils.UserData.unique_name==TEST_USER2)
        assert userdata.unique_name == TEST_USER
        assert userdata2.unique_name == TEST_USER2

        scored_track = db_utils.ScoredTrack.get(db_utils.ScoredTrack.title=='test_title')
        userscores = json.loads(scored_track.userscores)
        assert userscores[TEST_USER] == userscores[TEST_USER2]
        song = db_utils.ScoredTrack.get(db_utils.ScoredTrack.title=='test_title')
        our_score = json.loads(song.userscores)[TEST_USER2]
        assert our_score == cfg['scoring']['hits_per_track']
        track = db_utils.Playlist.get(db_utils.Playlist.title == 'test_title')
        assert int(track.score) == (cfg['scoring']['hits_per_track'] + cfg['scoring']['multiple_user']) * 2



def test_tracks_on_queue_get_made_into_playlist():
    party = PartyPlaylistForTesting(stdin=False)
    party.start()

    # make our contribution
    finder = MockFinder(TEST_USER, app=party, device='pc', db_name=TEST_CONTRIBUTION)
    finder.folders(paths=[SONG_FOLDER], default_paths=False)

    # push the contribution
    contribution_func.push_contribution(party.path_my_contribution,
                                        contribution=TEST_CONTRIBUTION,
                                        output_path=party.path_other_contribution,
                                        collection_path=party.path_collection,
                                        collection=TEST_COLLECTION,
                                        push_method='test')

    # gotta wait till threads do the stuff!
    time.sleep(10)

    with db_utils.connected_collection(os.path.join(party.path_collection, TEST_COLLECTION)):
        song = db_utils.ScoredTrack.get(db_utils.ScoredTrack.title=='test_title')
        assert song.title == 'test_title'
        assert song.album == 'test_album'
        assert song.artist == 'test_artist'
        assert song.genre == 'test_genre'


def test_vlc_player():
    pass

def test_music_source_youtube():
    pass

def test_songs_get_found_from_nfc():
    pass

def test_songs_get_found_from_wifi():
    pass

@pytest.mark.a
def test_make_songs_and_new_playlist_and_play():
    # New collection
    party = PartyPlaylistForTesting(stdin=False)
    party.start()

    # make our contribution
    home = os.path.expanduser("~")
    finder = MockFinder(TEST_USER, app=party, device='pc', db_name=TEST_CONTRIBUTION)
    finder.folders(paths=[os.path.join(home,'Music')], default_paths=False)

    # push the contribution
    contribution_func.push_contribution(party.path_my_contribution,
                                        contribution=TEST_CONTRIBUTION,
                                        output_path=party.path_other_contribution,
                                        collection_path=party.path_collection,
                                        collection=TEST_COLLECTION,
                                        push_method='test')

    # TODO locks for the main threads so i can tell when they are done!
    # TODO make it play music even when creating new...
    # TODo Tests for the player...
    time.sleep(50)
    import pdb;pdb.set_trace()




