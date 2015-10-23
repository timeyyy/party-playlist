import os
from time import strftime, gmtime
from contextlib import suppress

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
    def __init__(self, app, device, db_name, paths, default_paths=True):
        assert type(paths) in (tuple, list)

        self.device = device
        self.app = app
        self.db_path = self.setup_db(db_name)
        db = db_utils.connect_db(db_utils.UserContribution, self.db_path)
        if device == 'pc':
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
                self.folders(*def_paths)
            if paths:
                self.folders(*paths)

        elif device == 'android':
            pass


    def setup_db(self, db_name):
        '''returns absolute path of db, also handles none case'''
        if not db_name:
            db_name = strftime("%a, %d %b %Y %H-%M-%S.db", gmtime())
        db_path_name = os.path.join(self.app.path_my_contribution, db_name)
        db = db_utils.connect_db(db_utils.UserContribution, db_path_name)
        with suppress(peewee.OperationalError):
            db.create_table(db_utils.UserContribution)
        return db_path_name

    def add(self, song_info, source):
        if song_info.title and song_info.artist and song_info.duration:
            db_utils.UserContribution.create(title=song_info.title,
                                     artist=song_info.artist,
                                     album=song_info.album,
                                     genre=song_info.genre,
                                     length=song_info.duration,
                                     source=source)

    def spotify(self):
        pass

    def folders(self, *paths):
        extens = ('.mp3', '.wav', '.wma', '.ra', '.rm', '.ram', '.mid', '.ogg', '.aac', '.m4a', '.alac', '.ape',
                  '.flac', '.aiff')
        # import pdb;pdb.set_trace()
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


def push_contribution(app, contribution, output, collection, user):
    '''push contribution to another device over wifi or nfc'''
    file = os.path.join(app.path_my_contribution, contribution)
    shutil.move(file, os.path.join(output, file))

    db = connect_db(db_utils.Collection, collection)
    collectioninfo = db_utils.CollectionInfo.select()
    try:
        collectioninfo.users.append(user)
    except AttributeError:
        collectioninfo.users = [user]
    collectioninfo.save()


def get_contributions(app, collection):
    #TODO make collection into a propert =y of the app so the path auto gets made absolute
    collection = os.path.join(app.path_other_contribution, collection)
    connect_db(db_utils.Collection, collection)
    collectioninfo = db_utils.CollectionInfo.select()
    userdata_users = []
    for user in db_utils.UserData().select():
        userdata_users.append(user.name)
    for user in collectioninfo.users:
        # new contribution has been made!
        if user not in userdata_users:
            return collectioninfo.user_contributions
