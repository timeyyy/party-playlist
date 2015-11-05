import os
from time import strftime, gmtime
from contextlib import suppress
import shutil
import json
import time

import peewee
import hsaudiotag.auto

try:
    from . import db_utils
except SystemError:
    import db_utils

class FindMusic():
    '''finds tracks on mobile devices, computers and online accounts
    can tweak the folders to search before, and after you can see the tracks and which folders the came from,
    exclude any tracks/folders that are irrelevant before saving the users tracks'''
    def __init__(self, app, device, db_name):
        self.device = device
        self.app = app
        self.path = self.setup_db(db_name)


    def setup_db(self, db_name):
        '''returns absolute path of db, also handles none case'''
        if not db_name:
            db_name = strftime("%a, %d %b %Y %H-%M-%S.db", gmtime())
        db_path_name = os.path.join(self.app.path_my_contribution, db_name)
        with db_utils.connected_db(db_utils.UserContribution, db_path_name) as db:
            # with suppress(peewee.OperationalError):
            db.create_table(db_utils.UserContribution)
        with db_utils.connected_db(db_utils.UserData, db_path_name) as db:
            # with suppress(peewee.OperationalError):
            db.create_table(db_utils.UserData)
            db_utils.UserData.create(unique_name=self.get_unique_name())
        return db_path_name+'.db'

    @staticmethod
    def get_unique_name():
        #TODO
        return 'random_user_name'


    def add(self, song_info, source):
        if song_info.title and song_info.artist and song_info.duration:
            with db_utils.connected_db(db_utils.UserContribution, self.path):
                db_utils.UserContribution.create(title=song_info.title,
                                     artist=song_info.artist,
                                     album=song_info.album,
                                     genre=song_info.genre,
                                     length=song_info.duration,
                                     source=source)

    def spotify(self):
        pass

    def folders(self, paths, default_paths=True):
        # assert type(paths) in (tuple, list)
        if self.device == 'pc':
            home = os.path.expanduser("~")
            def_paths = []
            if os.name == 'posix':
                # TODO how to deal with folders in other languages
                def add_default_paths():
                    def_paths.append(os.path.join(home, 'Downloads'))
                    def_paths.append(os.path.join(home, 'Music'))
                    def_paths.append(os.path.join(home, 'Desktop'))
                    def_paths.append(os.path.join(home, 'Documents'))
            elif os.name == 'nt':
                def add_default_paths():
                    def_paths.append(os.path.join(home, 'Downloads'))
                    def_paths.append(os.path.join(home, 'Music'))
                    def_paths.append(os.path.join(home, 'Desktop'))
                    def_paths.append(os.path.join(home, 'Documents'))

            # delete any folders the user added that are already included by default
            if default_paths and paths:
                to_del = []
                for i, path in enumerate(paths):
                    with suppress(TypeError):
                        if path in default_paths:
                            to_del.append(i)
                with suppress(TypeError):
                    for index in to_del:
                        del paths[index]

            if default_paths:
                return
                add_default_paths()
                self._folders(*def_paths)
            if paths:
                self._folders(*paths)

        elif self.device == 'android':
            pass


    def _folders(self, *paths):
        extens = ('.mp3', '.wav', '.wma', '.ra', '.rm', '.ram', '.mid', '.ogg', '.aac', '.m4a', '.alac', '.ape',
                  '.flac', '.aiff')
        for path in paths:
            for root, dirs, files in os.walk(path):
                song_paths = [os.path.join(root, file) for file in files if os.path.splitext(file)[-1] in extens]
                if song_paths:
                    for song_path in song_paths:
                        song_info = hsaudiotag.auto.File(song_path)
                        self.add(song_info, source='hard_disk')

    def facebook(self):
        self.add(song_path=root_and_files, source='facebook')
    def youtube(self):pass
    def playlists(self):pass
    def soundcloud(self):pass
    def lastfm(self):pass
    def pandora(self):pass
    def rdio(self):pass


def push_contribution(my_contribution_path, contribution, output_path, collection_path, collection, push_method):
    '''push contribution to another device over wifi or nfc, or test for copy'''
    time.sleep(5)
    source = os.path.join(my_contribution_path, contribution+'.db')
    output = os.path.join(output_path, contribution+'.db')
    if push_method == 'wifi':
        pass
    elif push_method == 'nfc':
        pass
    elif push_method == 'test':
        print('copying {0}, to {1}'.format(source, output))
        shutil.copyfile(source, output)

    with db_utils.connected_db(db_utils.UserData, output):
        userdata = db_utils.UserData.get()
        user = userdata.unique_name


    with db_utils.connected_db(db_utils.CollectionInfo, os.path.join(collection_path, collection)):
        collection_info = db_utils.CollectionInfo.get()
        collection_info.users = json.loads(collection_info.users)
        collection_info.user_contributions = json.loads(collection_info.user_contributions)
        collection_info.users.append(user)
        collection_info.user_contributions.append(contribution)
        db_utils.save(collection_info)
    print('finished pushing contribution')


def get_new_contributions(collection_path, collection):
    # when a user pushes his songs his username gets added to CollectionInfo.users,
    # UserData.users will be different and we update it after adding the songs to the database
    with db_utils.connected_collection(os.path.join(collection_path, collection)):
        collection_info = db_utils.CollectionInfo.get()
        existing_users = []
        for user in db_utils.UserData().select():
            existing_users.append(user.unique_name)

    user_contributions = json.loads(collection_info.user_contributions)
    for i, user in enumerate(json.loads(collection_info.users)):
        # new contribution has been made!
        if user not in existing_users:
            yield user_contributions[i]


def delete_contribution(contribution_path, contribution):
    '''delete a playlist item either by id or by name'''
    try:
        try:
            int(contribution)
            for i, existing_contribution in enumerate(get_contributions(contribution_path)):
                if i == int(contribution):
                    os.remove(os.path.join(contribution_path, existing_contribution+'.db'))
                    print('Collection {0} deleted successfully'.format(contribution))
                    break
            else:
                raise FileNotFoundError
        except ValueError:
            os.remove(os.path.join(contribution_path, contribution+'.db'))
            print('Collection {0} deleted successfully'.format(contribution))
    except FileNotFoundError:
        print('Collection of name/id {0} could not be found for deletiong'.format(contribution))

def get_contributions(contribution_path):
    '''returns  ALL  contributions given either the other/mine path'''
    for root, dirs, files in os.walk(os.path.dirname(contribution_path)):
        for file in files:
            yield os.path.splitext(file)[0]

