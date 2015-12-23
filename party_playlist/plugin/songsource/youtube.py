# -*- coding: utf-8 -*-
import re
import string
from multiprocessing.pool import ThreadPool
from urllib.parse import urlparse, parse_qs
import unicodedata
import requests
import logging

import pafy

yt_api_endpoint = 'https://www.googleapis.com/youtube/v3/'
yt_key = 'AIzaSyAl1Xq9DwdE_KD4AtPaE4EJl3WZe2zCqg4'
session = requests.Session()

class MusicSource():
    def __init__(self, args):
        self.features = ('stream',)
    
    def load(self, track):
        '''Result it a list of dicts, each list item is a youtube hit,
        the dict contains the url as well as track info'''
        result = search_youtube(track.artist + track.title)
        return result
        
def resolve_track(track, stream=False):
    logging.debug("Resolving Youtube for track '%s'", track)
    if hasattr(track, 'uri'):
        return resolve_url(track.comment, stream)
    else:
        return resolve_url(track.split('.')[-1], stream)

def safe_url(uri):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    safe_uri = unicodedata.normalize('NFKD',str(uri))#.encode('ASCII', 'ignore')
    #~ print('safe',safe_uri)
    text=''.join(c for c in safe_uri if c in valid_chars)
    #~ print('ass')
    #~ print('TESX',text)
    scrubbed =  re.sub('\s+',' ',text)
    #~ print('after',scrubbed)
    return scrubbed.strip()

def resolve_url(url, stream=False):
    try:
        video = pafy.new(url)
        #~ uri = video.getbestaudio().url
        #~ return uri
        if not stream:
            uri = 'youtube:video/%s.%s' % (
                safe_url(video.title), video.videoid
            )
        else:
            print('audio gotten')
            uri = video.getbestaudio()
            if not uri:  # get video url
                uri = video.getbest()
            logging.debug('%s - %s %s %s' % (
                video.title, uri.bitrate, uri.mediatype, uri.extension))
            uri = uri.url
        if not uri:
            return
    except Exception as e:
        # Video is private or doesn't exist
        logging.info(e)
        return

    return uri


def search_youtube(q):
    query = {
        'part': 'id',
        'maxResults': 8,
        'type': 'video',
        'videoCategoryId':'music',
        'q': q,
        'key': yt_key
    }
    result = session.get(yt_api_endpoint+'search', params=query)
    data = result.json()

    #~ resolve_pool = ThreadPool(processes=16)
    playlist = [item['id']['videoId'] for item in data['items']] # also get name etc
    l2 = []
    for uid in playlist:
        try:
            video = pafy.new(uid)
            stream = video.getbestaudio()
            url = stream.url
            safe_url(video.title)
            l2.append(url)
        except:pass
    #~ print('finished')
    #~ return
    return l2
    #~ playlist = resolve_pool.map(resolve_url, playlist)
    #~ resolve_pool.close()
    #~ return [item for item in playlist if item]

def resolve_playlist(url):
    resolve_pool = ThreadPool(processes=16)
    logging.info("Resolving Youtube-Playlist '%s'", url)
    playlist = []

    page = 'first'
    while page:
        params = {
            'playlistId': url,
            'maxResults': 50,
            'key': yt_key,
            'part': 'contentDetails'
        }
        if page and page != "first":
            logging.debug("Get Youtube-Playlist '%s' page %s", url, page)
            params['pageToken'] = page

        result = session.get(yt_api_endpoint+'playlistItems', params=params)
        data = result.json()
        page = data.get('nextPageToken')

        for item in data["items"]:
            video_id = item['contentDetails']['videoId']
            playlist.append(video_id)

    playlist = resolve_pool.map(resolve_url, playlist)
    resolve_pool.close()
    #~ return [item for item in playlist if item]
    return [item for item in playlist if item]

if __name__ == '__main__':
    logging.basicConfig(filename= 'logging.log',
                                filemode='w',
                                level=logging.DEBUG,
                                format='%(asctime)s:%(levelname)s: %(message)s')    # one run
    
    
    #~ logging.debug(os.name)
    result = search_youtube('coheed and cambria')
    for i in result:
        logging.info(i)
    
