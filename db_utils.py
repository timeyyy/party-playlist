#~ from __future__ import print_function
#~ from __future__ import with_statement

import os
import time
from pprint import pprint
from contextlib import contextmanager
import peewee

DB_NAME = 'playlists.db'
DB_PATH = os.path.join(os.getcwd(), DB_NAME)

class FileExistsError(Exception):pass
	
playlist_db = peewee.SqliteDatabase(DB_PATH)	
playlist_db.connect() 
class PlaylistInfo(peewee.Model):
	'''Playlist name and settings for sorting tacks in the playlist'''
	name = peewee.CharField(unique=True)
	creation_date = peewee.CharField()
	event_name = peewee.CharField(null=1, unique=True)
	users = peewee.CharField(null=1)	
	scoring_multiple_user = peewee.CharField(null=1)
	scoring_hits_per_track = peewee.CharField(null=1)
	scoring_hits_per_album = peewee.CharField(null=1)
	scoring_profile = peewee.CharField(null=1)
	scoring_favourited = peewee.CharField(null=1)
	scoring_discovered = peewee.CharField(null=1)
	discovery = peewee.BooleanField(null=1)
	profile = peewee.CharField(null=1)
	class Meta:
		database = playlist_db 

def create_blank_db(test=0):
	'''Called by the deployment script'''
	if test:
		playlist_db.close()
		os.remove(DB_PATH)
	playlist_db.create_tables([PlaylistInfo])
  
class Track(peewee.Model):
	'''Loads the new tracks that are gotten from users'''
	title = peewee.CharField(null=1)
	artist = peewee.CharField(null=1) 
	album = peewee.CharField(null=1)
	genre = peewee.CharField(null=1)
	source = peewee.CharField(null=1)
	class Meta:
		database = None

def create_new(database, test=False):					
	### These get a new db every time, the db name is the playlist name	
	db = peewee.SqliteDatabase(database)	
	db.connect()
	class BaseModel(peewee.Model):
			class Meta:
				database = db
	
	class UserData(BaseModel):
		'''Collection Of User Data and the songs they have asscoated with them'''
		phone_name = peewee.CharField(unique=1)
		facebook_name = peewee.CharField(null=1) 
			
	class ScoredTrack(BaseModel):
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
	class PlayList(BaseModel):
		'''When the user changes the genre the final points here will just be changed'''
		playlist_name = peewee.CharField(null=1)
		title = peewee.CharField(null=1)
		artist = peewee.CharField(null=1)
		album = peewee.CharField(null=1)
		genre = peewee.CharField(null=1)
		score = peewee.CharField(null=1)
	if not test:			
		db.create_tables([UserData, ScoredTrack ,PlayList])
	else:
		pass
		#~ print('Test db recreating..')
		#~ db.close()
		#~ os.remove(database)
		#~ db = peewee.SqliteDatabase(database)
		#~ db.connect()
		#~ db.create_tables([UserData, ScoredTrack ,PlayList])
	return UserData, ScoredTrack ,PlayList

#~ class change_db():			DIDNT WORK zzz, cannot return from init.. wanted to use as a normal and context manager,
	#~ def __init__(self,orm_class, new_db):	Still dunno how to do it @contextmanager might be able to somethow
		#~ orm_class._meta.database = db
		#~ return orm_class
	#~ def __enter__(self,orm_class, new_db):
		#~ self.original_db = orm_class._meta.database
		#~ orm_class._meta.database = db
		#~ yield orm_class
	#~ 
	#~ def __exit__(self,*args):
		#~ orm_class._meta.database = self.original_db
@contextmanager
def changed_db(orm_class, new_db):
	original_db = orm_class._meta.database
	NEW_DB = peewee.SqliteDatabase(new_db)
	NEW_DB.connect()
	orm_class._meta.database = NEW_DB 
	yield orm_class
	#~ orm_class._meta.database = original_db
        

if __name__ == '__main__':		

	create_blank_db(test=1)
