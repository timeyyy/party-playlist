#~ from __future__ import print_function
#~ from __future__ import with_statement

import os
import time

import peewee

DB_NAME = 'music_data.db'
DB_PATH = os.path.join(os.getcwd(), DB_NAME)

def new(database = DB_PATH,overwrite = False):					
	#~ print("WE ARE IN",os.getcwd())
	if overwrite:								# Remove old db
		try:
			os.remove(database)
		except FileNotFoundError:
			#~ print("failed removal")
			pass
	elif os.path.isfile(database):				# if exists and no overwrite return 
		#~ print("IS FILE")
		return 0
		
	#~ print('CREATING NEW DB')
	db = peewee.SqliteDatabase(DB_PATH)	
	db.connect()
	db.create_tables([Track])
	
db = peewee.SqliteDatabase(DB_PATH)		

def load_track_db(android_db):
	db = peewee.SqliteDatabase(android_db)
	class Track(peewee.Model):
		title = peewee.CharField(null=1)
		artist = peewee.CharField(null=1) 
		album = peewee.CharField(null=1)
		genre = peewee.CharField(null=1)
		source = peewee.CharField(null=1)  
		class Meta:
			database = db
	return Track
			 
class BaseModel(peewee.Model):
    class Meta:
        database = db
        
class UserData(BaseModel):
	facebook_name = peewee.CharField(null=1) 
	phone_name = peewee.CharField(null=1) 
	fb_music = peewee.CharField(null=1) 
	hard_drive_music = peewee.CharField(null=1) 
	spotify_music = peewee.CharField(null=1) 

class PlaylistInfo(BaseModel):
	creation_date = peewee.CharField(null=1)
	event_name = peewee.CharField(null=1)
	playlist_name = peewee.CharField(null=1)
	users = peewee.CharField(null=1)	
	weight_multiple_user = peewee.CharField(null=1)
	weight_hits_per_user = peewee.CharField(null=1)
	weight_genre = peewee.CharField(null=1)
	weight_favourited = peewee.CharField(null=1)
	discovery = peewee.BooleanField(null=1)
	genre = peewee.CharField(null=1)
	
class PlaylistTrack(BaseModel):
	playlist_name = peewee.CharField(null=1)
	title = peewee.CharField(null=1)
	artist = peewee.CharField(null=1)
	album = peewee.CharField(null=1)
	genre = peewee.CharField(null=1)
	
class FinalPlayList(BaseModel):
	playlist_name = peewee.CharField(null=1)
	title = peewee.CharField(null=1)
	artist = peewee.CharField(null=1)
	weight = peewee.CharField(null=1)
	discovered = peewee.BooleanField(null=1)
	genre = peewee.CharField(null=1)
		
