import os
import json
import sys
import datetime

from party_playlist import db_utils, func

CFG = func.get_config()

'''
a collection or event is the main thing a user creates, it contains
all the settings and information about the music, from it playlists can
be played/exported and new songs added or delete from different sources/users
'''


def create_or_get_collection(collection_path, collection, load):
    '''Either creates a new playlist or setup an old one'''
    if load:
        if os.path.exists(os.path.join(collection_path, collection+'.db')):
            with db_utils.connected_db(db_utils.CollectionInfo, os.path.join(collection_path, collection)):
                collection_info = db_utils.CollectionInfo.get(db_utils.CollectionInfo.name == collection)
                if collection_info.users:
                    # its a list saved as a string so turning it into a python object
                    collection_info.users = json.loads(collection_info.users)
            return collection_info
        else:
            print()
            print('Playlist Does not exist!')
            print('Use the list command to view playlists or new to create it !')
            print()
            # TODO this sys exit only works for cli
            sys.exit()
            return
    else:
        # creating new
        for existing_collection in get_collections(collection_path):
            if existing_collection == collection:
                print()
                print('Collection already exists')
                print('Either delete the playlist, or use the load command')
                print()
                # Todo shutdown program here..
                return
        collection_info = new_collection(collection_path, collection)
        return collection_info


def new_collection(collection_path, collection):
    '''setup the database with the correct tables and return orm objects'''
    with db_utils.connected_collection(os.path.join(collection_path, collection)) as db:
        db.create_tables([db_utils.CollectionInfo,
                          db_utils.UserData,
                          db_utils.ScoredTrack,
                          db_utils.Playlist])

        collection_info = db_utils.CollectionInfo.create(name=collection,
                                     creation_date=datetime.datetime.now(),
                                     event_name=None,
                                     users=json.dumps([]),
                                     user_contributions=json.dumps([]),
                                     discovery=CFG['playing']['discovery_mode'],
                                     profile=CFG['playing']['profile'],
                                     scoring_profile=CFG['scoring']['profile'],
                                     scoring_multiple_user=CFG['scoring']['multiple_user'],
                                     scoring_hits_per_track=CFG['scoring']['hits_per_track'],
                                     scoring_hits_per_album=CFG['scoring']['hits_per_album'],
                                     scoring_discovered=CFG['scoring']['discovered'],
                                     scoring_favourited=CFG['scoring']['favourited'])
    print()
    print('New collection {0} created succesfully'.format(collection))
    print()
    # return collection_info


def list_collection(collection_path, collection=None):
    print()
    if not collection:
        print('All Collections.. (use the id value for getting more info or deleting)')
        for i, existing_collection in enumerate(get_collections(collection_path)):
            print(i, existing_collection)
        print()
    else:
        try:
            try:
                int(collection)
                for i, existing_collection in enumerate(get_collections(collection_path)):
                    if i == int(collection):
                        with db_utils.connected_db(db_utils.CollectionInfo, os.path.join(collection_path, existing_collection)):
                            collection_info = db_utils.CollectionInfo.get()
            except ValueError:
                with db_utils.connected_db(db_utils.CollectionInfo, os.path.join(collection_path, collection)):
                    collection_info = db_utils.CollectionInfo.get()
            print('Data for Collection :: ', collection_info.name)
            print()
            for key, value in collection_info._data.items():
                print(key,':    ',value)
        except Exception as err:
            if 'DoesNotExist' in str(err.__class__):
                print('That collection does not exist...')
            else:
                raise err


def delete_collection(collection_path, collection):
    '''delete a playlist item either by id or by name only the users contributions can be deleted,
    contribution that have been pushed TODO'''
    try:
        try:
            int(collection)
            for i, existing_collection in enumerate(get_collections(collection_path)):
                if i == int(collection):
                    os.remove(os.path.join(collection_path, existing_collection+'.db'))
                    print('Collection {0} deleted successfully'.format(collection))
                    break
            else:
                raise FileNotFoundError
        except ValueError:
            os.remove(os.path.join(collection_path, collection+'.db'))
            print('Collection {0} deleted successfully'.format(collection))
    except FileNotFoundError:
        print('Collection of name/id {0} could not be found for deletion'.format(collection))
        raise


def get_collections(collection_path):
    '''returns  all  collections'''
    for root, dirs, files in os.walk(collection_path):
        for file in files:
            yield os.path.splitext(file)[0]


# def get_collection_name(collection_path, collection):
#     '''returns name of collection as saved in the database, it's possible that the name is the same as the
#     database name but whatever'''
#     db_utils.connect_db(db_utils.Collection, os.path.join(collection_path, collection))
#     import pdb;pdb.set_trace()
#     row = db_utils.CollectionInfo.get()
#     return row.name
