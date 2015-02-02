from __future__ import print_function
from __future__ import with_statement
import os
from pprint import pprint

import mutagen

import db_utils

def hard_drive(start_path, viewer):
	'''
	Recursivley searchs folders and 
	'''
	def get_info(start_path):
		for root, dirs, files in os.walk(start_path):
			#~ path = root.split('/')
			#~ print (len(path) - 1) *'---' , os.path.basename(root)       
			music = (os.path.join(root, file) for file in files if file.split('.')[-1] in ('mp3','wma'))
			for song in music:
				s_info = mutagen.File(song, easy=True)		# Gueses the file type and all that
				if s_info.info.length/60 < 12:				# Songs must be less than 12 minutes long, filter out podcasts etc
					
					title = s_info.get('title', None)		
					print(title)
					artist = s_info.get('artist',None)
					album = s_info.get('album',None)
					genre = s_info.get('genre', None)
					yield title, artist, album, genre, root
					
	for title, artist, album, genre, root in get_info(start_path):
		if title: title = title[0]
		if artist: artist = artist[0]
		if album: album = album[0]
		if genre: genre = genre[0]
		new_track = db_utils.Track(title=title, artist=artist, album=album, genre=genre,
									source = 'hard_drive - {0}'.format(root))
		new_track.save()
		viewer.text = '{0}\n{1} :: {2}'.format(viewer.text, artist, title)
