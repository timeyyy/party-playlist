from __future__ import print_function
from __future__ import with_statement

import os
import time

import peewee

DB_NAME = 'musiclist.db'
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

class Track(peewee.Model):
	title = peewee.CharField(null=1)
	artist = peewee.CharField(null=1) 
	album = peewee.CharField(null=1)
	genre = peewee.CharField(null=1)
	source = peewee.CharField(null=1)  
	class Meta:
		database = db
