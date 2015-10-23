'''
a collection or event is the main thing a user creates, it contains
all the settings and information about the music, from it playlists can
be played/exported and new songs added or delete from different sources/users
'''

import os

import db_utils


def setup(database, create=True, test=False):
    '''setup the database with the correct tables and return orm objects'''
    db = connect_db(Collection, database)
    if create:
        db.create_tables([db_utils.CollectionInfo,
                          db_utils.UserData,
                          db_utils.ScoredTrack,
                          db_utils.PlayList])


def _new_collection(new_name, test=False):

    db = db_utils.connect_db(Collection, new_name)

    # Creating Tables if new database
    collection.setup(collection, create=not load, test=test)
    db = db_utils.connect_db(db_utils.Collection, collection)

    try:
        collection_info = db_utils.PlaylistInfo.create(name=new_name,
                                                     creation_date=datetime.datetime.now(),
                                                     event_name=None,
                                                     users=None,
                                                     discovery=CFG['playing']['discovery_mode'],
                                                     profile=CFG['playing']['profile'],
                                                     scoring_profile=CFG['scoring']['profile'],
                                                     scoring_multiple_user=CFG['scoring']['multiple_user'],
                                                     scoring_hits_per_track=CFG['scoring']['hits_per_track'],
                                                     scoring_hits_per_album=CFG['scoring']['hits_per_album'],
                                                     scoring_discovered=CFG['scoring']['discovered'],
                                                     scoring_favourited=CFG['scoring']['favourited'])
    except Exception as err:
        if 'IntegrityError' in str(err.__class__):
            if not test:
                raise err
        else:
            raise err
        #~ print(' TException Caught',err)
        playlist_info = db_utils.PlaylistInfo.get(db_utils.PlaylistInfo.name==new_name)
    return playlist_info


def create_or_get_collection(collection, load, test):
    '''Either creates a new playlist or returns an old one'''
    try:
        collection_info = db_utils.CollectionInfo.get(db_utils.CollectionInfo.name == collection)
        if collection_info.users:
            collection_info.users = json.loads(collection_info.users)   # its a list saved as a string so turning it into a python object
        if not load and not test:
            print()
            print('Playlist already exists')
            print('Either: --test to ignore, delete the playlist, or use the load command')
            print()
            return

    except Exception as err:
        print('DoesNotExist!!!!!!!')
        if 'DoesNotExist' not in str(err.__class__):
            raise err
        elif load:
            print()
            print('Playlist Does not exist!')
            print('Use the list command to view playlists or new to create it !')
            print()
            sys.exit()
        else:
            collection_info = _new_collection(collection, test=test)
    return collection_info


def list_collection(name=None):
    print()
    if not name:
        print('All Playlists.. (use the id value for getting more info or deleting)')
        for playlist in PlaylistInfo.select():
            print(playlist.id,  playlist.name)
        print()
    else:
        try:
            try:
                int(name)
                playlist = PlaylistInfo.get(id=name)
            except ValueError:
                playlist = PlaylistInfo.get(name=name)
            print('Data for Playlist :: ', playlist.name)
            print()
            for key,value in playlist._data.items():
                print(key,':    ',value)
        except Exception as err:
            if 'DoesNotExist' in str(err.__class__):
                print('That playlist does not exist...')
            else:
                raise err


def delete_collection(name):
    '''delete a playlist item either by id or by name'''
    try:
        try:
            int(name)
            playlist = PlaylistInfo.get(id=name)
        except ValueError:
            playlist = PlaylistInfo.get(name=name)
        playlist.delete_instance()
    except Exception as err:
        print('Playlist of name/id {0} could not be found for deletiong'.format(name))
    else:
        print('Playlist {0} deleted successfully'.format(name))


def get_collections(app):
    '''returns all collections'''
    for root, dirs, files in os.walk(app.path_collections):
        root_and_files = (os.path.join(root, file) for file in files)
        for path in root_and_files:
            yield path


def get_collection_name(collection):
    '''returns name of collection'''
    db_utils.connect_db(collection)
    row = db_utils.CollectionInfo.get()
    return row.name
