from collections import defaultdict
import json
import os

import yaml
import peewee

try:
    import db_utils
    import func
except SystemError:
    from .db_utils import *
    from .func import *


'''
edge cases:
    a user has pushed the wrong contribution, in which case roll back his previous changes and add the new one
    a user tries to push the same contribution twice
'''


def get_least_played_track():
    pass


def score_tracks(contribution_path, contribution, user, cfg):
    db = db_utils._connect_db(db_utils.UserContribution, os.path.join(contribution_path, contribution))
    uc = db_utils.UserContribution
    hits = defaultdict(int)
    for track in uc.select().order_by(uc.artist, uc.album, uc.title):
        if "hard_disk" in track.source:
            hits[track.title] = hits[track.title] + cfg['scoring']['hits_per_track']
        elif "facebook" in track.source:
            hits[track.album] = hits[track.album] + cfg['scoring']['hits_per_album']
        else:
            raise Exception('Track source is of wrong type...: {0}'.format(track.source))

    for track in uc.select().order_by(uc.artist, uc.album, uc.title):
        if track.title:
            SCORE_TYPE = track.title
        else:
            SCORE_TYPE = track.album
        try:
            # TOdo and the artist is the same
            scored_track = db_utils.ScoredTrack.get(db_utils.ScoredTrack.title==track.title)
        except Exception as err:
            if not 'does not exist' in str(err):
                raise err
            userscores = {user.unique_name: hits[SCORE_TYPE]}
            db_utils.ScoredTrack.create(userscores=json.dumps(userscores),
                                        title=track.title,
                                        artist=track.artist,
                                        album=track.album,
                                        genre=track.genre)
        else:
            userscores = json.loads(scored_track.userscores)
            if not userscores.get(user.unique_name):
                userscores[user.unique_name] = hits[SCORE_TYPE]
                scored_track.userscores = userscores
                db_utils.save(scored_track)
            else:
                # todo NEED TO STOP SAME USER FROM PUSHING RESULTS AGAIN
                pass
    db.close()

def calculate_playlist_score(profile, cfg):
    for scored_track in db_utils.ScoredTrack.select():
        user_track_points = 0
        userscores = json.loads(scored_track.userscores)
        for points in userscores.values():
            user_track_points += points
        multi_user_points = len(json.loads(scored_track.userscores)) * cfg['scoring']['multiple_user']
        if scored_track.discovered:
            discovery_points = cfg['scoring']['discovered']
        else:
            discovery_points = 0
        try:
            if scored_track.genre in profile:
                profile_points = cfg['scoring']['profile']
            else:
                profile_points = 0
        except TypeError:
            profile_points = 0

        scored_track.multi_user_bonus = multi_user_points
        scored_track.discovered_bonus = discovery_points
        scored_track.profile_bonus = profile_points
        scored_track.save()

        score = user_track_points + multi_user_points + discovery_points + profile_points

        update_playlist(scored_track, score)
        print('finished updating')


def update_playlist(scored_track, score):
    '''update the playlist track with new score or create new'''
    #TODO and also same artist..
    # todo best way on going through all db entries
    print('updating playlist..{0}'.format(scored_track.title))
    update_query = db_utils.Playlist.update(score=score).where(db_utils.Playlist.title == scored_track.title)
    count_of_updated_rows = update_query.execute()
    if not count_of_updated_rows:
        track = db_utils.Playlist.create(title=scored_track.title,
                                         album=scored_track.album,
                                         artist=scored_track.album,
                                         genre=scored_track.genre,
                                         score=score,
                                         times_played=0)
        track.save()

def process_tracks(collection_path, collection, contribution_path, contribution, cfg, arg_profile=0):
    '''
    a contribution is passed in to be updated/added to our collection
    we calculate based on the collection settings how many points to give.
    the playlist gets remade from the update scored tracks.
    at the end we add an entry to UserData from collection_info.users so we know that its been added

    update = True if the contirbution already exists and is being updated
    '''

    # If our playlist has been in use for over a certain time make a new one
    # else:
    #     creation_time = playlist_info.creation_date
    #     creation_time = datetime.datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S.%f")
    #     now = datetime.datetime.now()
    #     time_diff = now - creation_time
    #     hours_diff = time_diff.total_seconds()/3600
    #
    #     if hours_diff > cfg['playing']['playlist_active_time']:
    #         playlist_info = create_new_playlist(playlist_db_name, test=test)

    # if arg_timeout:
    #     cfg['playing']['playlist_active_time'] = arg_timeout
    if arg_profile:
        cfg['playing']['profile'] = arg_profile

    # the new user to be added
    with db_utils.connected_db(db_utils.UserData, os.path.join(contribution_path, contribution)):
        user = db_utils.UserData.get()

    with db_utils.connected_collection(os.path.join(collection_path, collection)):
        score_tracks(contribution_path, contribution, user, cfg)

        if cfg['playing']['discovery_mode'] == True:
            print('discoverying new tracks')

        if cfg['playing']['profile'] == 'dynamic':
            print('The profile is being generated dynamically')
        else:
            profile = cfg['playing']['profile']

        calculate_playlist_score(profile, cfg)

        db_utils.UserData.create(unique_name=user.unique_name)
