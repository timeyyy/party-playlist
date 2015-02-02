import os
import logging
import peewee

DB_NAME = 'musiclist.db'
DB_PATH = os.path.join(DB_PATH, DB_NAME)


def new(database = DB_PATH,overwrite = False):					
	if overwrite:								# Remove old db
		try:
			os.remove(database)
		except FileNotFoundError:
			pass
			
	elif os.path.isfile(database):				# if exists and no overwrite return 
		return 0
		
	logging.info('CREATING NEW DB')
	db = peewee.SqliteDatabase(DB_PATH)	
	db.connect()
	db.create_tables([db_utils.Track])
		
class Track(peewee.Model):
	title = peewee.CharField()
	artist = peewee.CharField() 
	album = peewee.CharField()
	genre = peewee.CharField()
	source = peewee.CharField()  
	class Meta:
		database = db
		
		
import sqlalchemy as sqa
from sqlalchemy.ext.declarative import declarative_base
from sqlite3 import dbapi2 as sqlite

Base = declarative_base()

class Song(Base):	
	#~ def __init__(self, table):		#Table is where it comes from
	__tablename__ = 'all_info'
	id = sqa.Column(sqa.Integer, primary_key=True)
	title = sqa.Column(sqa.String)
	artist = sqa.Column(sqa.String) 
	album = sqa.Column(sqa.String)
	genre = sqa.Column(sqa.String)
	source = sqa.Column(sqa.String)  # fb, device hd, (also give folder), pandora, spotify etc
	
	def __repr__(self):
		return "{0} :: {1} :: {2} :: {3}".format(self.artist,self.title,self.album,self.genre)

def make_db(engine):
	Base.metadata.create_all(engine) 
