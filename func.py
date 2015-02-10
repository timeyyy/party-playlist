import sys
import os
from pprint import pprint
from collections import defaultdict
import yaml
import datetime
import operator
import json

import peewee

import db_utils
from db_utils import PlaylistInfo

with open("config.conf", 'r') as ymlfile:
    CFG = yaml.load(ymlfile)

def create_new_playlist(new_name, test=False):
	try:
		playlist_info = PlaylistInfo.create(name=new_name,
									creation_date=datetime.datetime.now(),
									event_name=None,
									users=None,
									discovery=CFG['playing']['discovery_mode'],
									profile=CFG['playing']['profile'],
									scoring_profile=CFG['scoring']['profile'],
									scoring_multiple_user=CFG['scoring']['multiple_user'],
									scoring_hits_per_track=CFG['scoring']['hits_per_track'],
									scoring_hits_per_album=CFG['scoring']['hits_per_album'],
									scoring_discovered=CFG['scoring']['discovered'],
									scoring_favourited=CFG['scoring']['favourited'])
	except Exception as err:
		if 'IntegrityError' in str(err.__class__):
			if not test:
				raise err 
		else:
			raise err
		#~ print(' TException Caught',err)
		playlist_info = db_utils.PlaylistInfo.get(db_utils.PlaylistInfo.name==new_name)
	return playlist_info
	
def process_tracks(playlist_db_name, load=False, arg_timeout=False, arg_profile=False, test=False):
	#Setting up cfg and formatting variable names
	if '.db' in playlist_db_name:
		playlist_db_name = playlist_db_name.split('.')[0]
	if arg_timeout:
		CFG['playing']['playlist_active_time'] = arg_timeout
	if arg_profile:
		CFG['playing']['profile'] = arg_profile
	# Loading or creating Playlist
	try:
		playlist_info = PlaylistInfo.get(PlaylistInfo.name == playlist_db_name)
		if playlist_info.users:
			playlist_info.users = json.loads(playlist_info.users)	# its a list saved as a string so turning it into a python object
		if not load and not test:
			print()
			print('Playlist already exists')
			print('Either: --test to ignore, delete the playlist, or use the load command') 
			print()
			sys.exit()		

	except Exception as err:
		print('DoesNotExist!!!!!!!')
		if 'DoesNotExist' not in str(err.__class__):
			raise err
		elif load:
			print()
			print('Playlist Does not exist!')
			print('Use the list command to view playlists or new to create it !')
			print()
			sys.exit()
		else:
			playlist_info = create_new_playlist(playlist_db_name, test=test)
	# If our playlist has been in use for over a certain make a new one		
	else:
		creation_time = playlist_info.creation_date
		creation_time = datetime.datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S.%f")
		now = datetime.datetime.now()
		time_diff = now - creation_time
		hours_diff = time_diff.total_seconds()/3600
		
		if hours_diff > CFG['playing']['playlist_active_time']: 
			playlist_info = create_new_playlist(playlist_db_name, test=test)
		
	# Creating or loading the Database 
	UserData, ScoredTrack, PlayList = db_utils.setup_orm(playlist_db_name+'.db', create=not load, test=test)
	
	# Calculating Points for tracks 
	filenames = []						# Get all files in the cwd		#http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
	for root, dirs, files in os.walk('new_track_info'):	# add to tims tools for listing files...
		root_and_files = [os.path.join(root, file) for file in files]
		filenames.extend(root_and_files)
		break
	
	for db in filenames:			# read the tracks in each db, each db was created by one user so get that users name
		hits = defaultdict(int)
		user = db.split('-')[-1]
		user = user.split('.')[0]
		# Save the user data
		try:
			user_data = UserData.create(phone_name=user)
		except peewee.IntegrityError:	# already exists
			pass
		with db_utils.changed_db(db_utils.Track,os.path.join(os.getcwd(),db)) as T:			# first time with orms, im changing the db of the orm class
			for track in T.select().order_by(T.artist,T.album,T.title):
				if "hard_drive" in track.source:	
					hits[track.title] = hits[track.title] + CFG['scoring']['hits_per_track']
				elif "facebook" in track.source:
					hits[track.album] = hits[track.album] + CFG['scoring']['hits_per_album']
			# Save The users Scores
			def first_time_adding():	# NEED TO STOP SAME USER FROM PUSHING RESULTS AGAIN
				for track in T.select().order_by(T.artist,T.album,T.title):
					if track.title:
						SCORE_TYPE = track.title
					else:
						SCORE_TYPE = track.album		
					USERSCORES = {user:hits[SCORE_TYPE]}
					ScoredTrack.create(userscores=json.dumps(USERSCORES),
												title=track.title,
												artist=track.artist,
												album=track.album,
												genre=track.genre)
			try:
				if user not in playlist_info.users:
					first_time_adding()
			except TypeError:
				playlist_info.users = []
				first_time_adding()
			else:
				# Modify exisiting scored Tracks
				print('User already added tracks!!!, need to modify either figure out a way to do it server side, otherwise client side easier')
				print('atm just rehashing everything..')
				first_time_adding()
			finally:
				if user not in playlist_info.users:
					#~ print('adding new user comeon ')
					playlist_info.users.append(user)
					playlist_info.users = json.dumps(playlist_info.users)
					playlist_info.save()
			
			### Rehsashing all the tracks... 
			if CFG['playing']['discovery_mode'] == True:
				print('discoverying new tracks')
			
			if CFG['playing']['profile'] == 'dynamic':
				print('The profile is being generated dynamically')
				#~ profile = CFG['profiles']['normal']
			else:
				profile = CFG['playing']['profile'] # atm its set to the normal profile
					
			for scored_track in ScoredTrack.select():
				user_track_points = 0
				USERSCORES = json.loads(scored_track.userscores)
				for points in USERSCORES.values():
					user_track_points + points
				multi_user_points = len(scored_track.userscores) * CFG['scoring']['multiple_user']	# Calculate points for multipleusers
				if scored_track.discovered:
					discovery_points = CFG['scoring']['discovered']
				else:
					discovery_points = 0
				try:
					if scored_track.genre in profile:
						profile_points = CFG['scoring']['profile']
					else:
						profile_points = 0
				except TypeError:
					profile_points = 0
		
				scored_track.multi_user_bonus = multi_user_points
				scored_track.discovered_bonus = discovery_points
				scored_track.profile_bonus = profile_points
				scored_track.save()
				
				score = user_track_points + multi_user_points + discovery_points + profile_points
				
				#Need to only create if its not already in there, otherwise update
				new_playlist_track = PlayList.create(title=scored_track.title,
												artist=scored_track.artist,
												album=scored_track.album,
												genre=scored_track.genre,
												score=score)
												 
				
			# PlayList
			#~ sorted_by_values = sorted(total_points.items(), key=operator.itemgetter(1)) # http://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
			#~ new_playlist = PlayList()

if __name__ == '__main__':
	#~ test()
	pass



