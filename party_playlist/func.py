import sys
import os
from pprint import pprint
from collections import defaultdict
import yaml
import datetime
import operator
import json
import shutil

import peewee

import collection
try:
    from .db_utils import *
except SystemError:
    import db_utils
with open("config.conf", 'r') as ymlfile:
    CFG = yaml.load(ymlfile)


def process_tracks(app, collection, contribution, load=False, arg_timeout=False, arg_profile=False, test=False):
    #Setting up cfg and formatting variable names

    # If our playlist has been in use for over a certain make a new one
    # else:
    #     creation_time = playlist_info.creation_date
    #     creation_time = datetime.datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S.%f")
    #     now = datetime.datetime.now()
    #     time_diff = now - creation_time
    #     hours_diff = time_diff.total_seconds()/3600
    #
    #     if hours_diff > CFG['playing']['playlist_active_time']:
    #         playlist_info = create_new_playlist(playlist_db_name, test=test)

    if arg_timeout:
        CFG['playing']['playlist_active_time'] = arg_timeout
    if arg_profile:
        CFG['playing']['profile'] = arg_profile


    # Each user who contriubtes songs copies their music over in a db...
    # Calculating Points for tracks, getting all databases in our playlist folder..
    databases_to_add = []
    # playlist_path = os.path.join('new_track_info', playlist_db_name)
    for root, dirs, files in os.walk('new_track_info'):
        root_and_files = [os.path.join(root, file) for file in files]
        databases_to_add.extend(root_and_files)
        break
    
    for database in databases_to_add:
        hits = defaultdict(int)
        user = db.split('-')[-1]
        user = user.split('.')[0]
        # Save the user data
        try:
            user_data = db_utils.UserData.create(phone_name=user)
        except peewee.IntegrityError:   # already exists
            pass
        uc = db_utils.UserContribution
        db = db_utils.connect_db(uc, os.path.join(os.getcwd(), database))

        for track in uc.select().order_by(uc.artist,uc.album,uc.title):
            if "hard_drive" in track.source:
                hits[track.title] = hits[track.title] + CFG['scoring']['hits_per_track']
            elif "facebook" in track.source:
                hits[track.album] = hits[track.album] + CFG['scoring']['hits_per_album']

        # Save The users Scores
        def first_time_adding():    # NEED TO STOP SAME USER FROM PUSHING RESULTS AGAIN
            for track in uc.select().order_by(uc.artist,uc.album,uc.title):
                if track.title:
                    SCORE_TYPE = track.title
                else:
                    SCORE_TYPE = track.album
                USERSCORES = {user:hits[SCORE_TYPE]}
                db_utils.ScoredTrack.create(userscores=json.dumps(USERSCORES),
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

        for scored_track in db_utils.ScoredTrack.select():
            user_track_points = 0
            USERSCORES = json.loads(scored_track.userscores)
            for points in USERSCORES.values():
                user_track_points + points
            multi_user_points = len(scored_track.userscores) * CFG['scoring']['multiple_user']  # Calculate points for multipleusers
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
            
def next_tracks(playlist_db_name, number):
    '''Returns tracks to be played!'''
    if number == 'all':
        number = 0.1    # will never equal this so for loop will grab all tracks
    #TODO make sure playlist_db_name is sanitzied etc
    db = db_utils.connect_db(Collection, playlist_db_name)
    tracks = []
    #~ PlayList.playlist_name = ''
    for i, track in enumerate(db_utils.PlayList.select().order_by(db_utils.PlayList.score)):
        if i == number:
            break
        tracks.append(track)
    return tracks

def get_input(on_false=lambda:0, **commands):
    ''' on false is a command to be run when a false command is input
    pass keys and commands that will be called when the user enters that comand'''
    while 1:
        try:
            data = input()
        except KeyboardInterrupt:
            return
        except IOError:
            data = 0 # unfortunaley input fucks up when uswing pdb sometimes i think XD TODO delete

        if commands.get(data):
            commands[data]()
        else:
            on_false()

class RegisterCommands(dict):
    def add(self, function, cmd, *aliases):
        '''for registering commands for get_input above'''
        self[cmd] = function
        if aliases:
            for alias in aliases:
                self[alias] = function




def test():
    '''testing adding a new contribution to a playlist'''

'''

'''
