import os
from contextlib import contextmanager
import json
import _thread as thread
import gc

import peewee

#when we change the orm database if another thread was writing to another db the change will take plkace in the wrong db..
LOCK = thread.allocate_lock()

# '''
# a few simple db wrappers for peewee and our orm classes
# '''

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
    name = peewee.CharField(unique=1)
    creation_date = peewee.CharField()
    event_name = peewee.CharField(null=1, unique=1)
    users = peewee.CharField() # New users get added here ! this is the unique_name in UserData
    user_contributions = peewee.CharField() # Name of contribution that a user pushed !
    scoring_multiple_user = peewee.CharField()
    scoring_hits_per_track = peewee.CharField()
    scoring_hits_per_album = peewee.CharField()
    scoring_profile = peewee.CharField()
    scoring_favourited = peewee.CharField()
    scoring_discovered = peewee.CharField()
    discovery = peewee.BooleanField()
    profile = peewee.CharField()

class UserData(Collection):
    '''Collection Of User Data that have already been processed into the ScoredTrack'''
    login = peewee.CharField(null=1)
    unique_name = peewee.CharField(unique=1)
    phone_name = peewee.CharField(null=1)
    facebook_name = peewee.CharField(null=1)
    computer_name = peewee.CharField(null=1)

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

class Playlist(Collection):
    '''When the user changes the genre the final points here will just be changed
    this is build up continuosly as the songs are added'''
    playlist_name = peewee.CharField(null=1)
    title = peewee.CharField(null=1)
    artist = peewee.CharField(null=1)
    album = peewee.CharField(null=1)
    genre = peewee.CharField(null=1)
    score = peewee.CharField(null=1)
    times_played = peewee.CharField()


def _connect_db(orm_class, database):
    '''change db of a peewee orm class'''
    if os.path.splitext(database)[-1] != '.db':
        database = database + '.db'
    db = peewee.SqliteDatabase(database, threadlocals=True)
    db.connect()
    orm_class._meta.database = db
    return db

@contextmanager
def connected_db(orm_class, database):
    with LOCK:
        db = _connect_db(orm_class, database)
        yield db
        db.close()
        gc.collect()

def _connect_collection(database):
    '''connects all our tables to the correct database'''
    if os.path.splitext(database)[-1] != '.db':
        database = database + '.db'
    db = peewee.SqliteDatabase(database, threadlocals=True)
    db.connect()
    CollectionInfo._meta.database = db
    UserData._meta.database = db
    ScoredTrack._meta.database = db
    Playlist._meta.database = db
    return db

@contextmanager
def connected_collection(database):
    with LOCK:
        db = _connect_collection(database)
        try:
            yield db
        finally:
            db.close()
            gc.collect()

def save(instance):
    '''dumps lists and so on into strs for saving with databases using json'''
    dumped = {}
    for key, value in instance._data.items():
        if type(value) in (tuple, dict, list):
            dumped[key] = json.dumps(value)
    instance._data.update(dumped)
    instance.save()



