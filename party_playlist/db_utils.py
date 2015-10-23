'''
a few simple db wrappers for peewee and our orm classes
'''
import os

import peewee

class FileExistsError(Exception):pass
    
def create_blank_db(test=0):
    '''Called by the deployment script'''
    if test:
        playlist_db.close()
        os.remove(DB_PATH)
    playlist_db.create_tables([PlaylistInfo])


class UserContribution(peewee.Model):
    '''Loads the new tracks that are gotten from users'''
    title = peewee.CharField(null=1)
    artist = peewee.CharField(null=1)
    album = peewee.CharField(null=1)
    genre = peewee.CharField(null=1)
    length = peewee.CharField(null=1)
    source = peewee.CharField(null=1)
    class Meta:
        database = None

class Collection(peewee.Model):
    class Meta:
        database = None

class CollectionInfo(Collection):
    '''Settings for sorting tacks in the playlist'''
    name = peewee.CharField(unique=True)
    creation_date = peewee.CharField()
    event_name = peewee.CharField(null=1, unique=True)
    users = peewee.CharField(null=1)# New users get added here !
    user_collections = peewee.CharField(null=1)# New users get added here !
    scoring_multiple_user = peewee.CharField(null=1)
    scoring_hits_per_track = peewee.CharField(null=1)
    scoring_hits_per_album = peewee.CharField(null=1)
    scoring_profile = peewee.CharField(null=1)
    scoring_favourited = peewee.CharField(null=1)
    scoring_discovered = peewee.CharField(null=1)
    discovery = peewee.BooleanField(null=1)
    profile = peewee.CharField(null=1)

class UserData(Collection):
    '''Collection Of User Data that have already been processed into the ScoredTrack'''
    phone_name = peewee.CharField(unique=1)
    facebook_name = peewee.CharField(null=1)

class ScoredTrack(Collection):
    '''Users contribution to a song is shown here'''
    title = peewee.CharField(null=1)
    artist = peewee.CharField(null=1)
    album = peewee.CharField(null=1)
    genre = peewee.CharField(null=1)
    discovered = peewee.BooleanField(default=0)
    userscores = peewee.CharField(null=1)
    multiuser_bonus =  peewee.CharField(null=1)
    profile_bonus = peewee.CharField(null=1)
    discovered_bonus = peewee.BooleanField(null=1)

class PlayList(Collection):
    '''When the user changes the genre the final points here will just be changed
    this is build up continuosly as the songs are added'''
    playlist_name = peewee.CharField(null=1)
    title = peewee.CharField(null=1)
    artist = peewee.CharField(null=1)
    album = peewee.CharField(null=1)
    genre = peewee.CharField(null=1)
    score = peewee.CharField(null=1)

def connect_db(orm_class, database):
    '''change db of a peewee orm class, best way is to make all tables of a database a subclass and change the parent'''
    if os.path.splitext(database)[-1] != '.db':
        database = database + '.db'

    db = peewee.SqliteDatabase(database, threadlocals=True)
    db.connect()
    orm_class._meta.database = db
    return db
