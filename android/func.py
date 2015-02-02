from __future__ import print_function
from __future__ import with_statement
import os
from pprint import pprint

import mutagen



def hard_drive(path):
	'''
	Recursivley searchs folders and 
	'''
	def get_info(path):
		for root, dirs, files in os.walk(start_path):
			#~ path = root.split('/')
			#~ print (len(path) - 1) *'---' , os.path.basename(root)       
			music = (file for file in files if file.split('.')[-1] in ('mp3','wma'))
			for song in music:
				s_info = mutagen.File(song, easy=True)		# Gueses the file type and all that
				if s_info.info.length/60 < 12:				# Songs must be less than 12 minutes long, filter out podcasts etc
					title = s_info.get('title', None)			
					artist = s_info.get('artist',None)
					album = s_info.get('album',None)
					genre = s_info.get('genre', None)
					return title, artist, album, genre
					
	for title, artist, album, genre in get_info(path):
		new_track = db_utils.Track(title=title, artist=artist, album=album, genre=genre,
									source = 'hard_drive - {0}'.format(path))
		new_track.save()

