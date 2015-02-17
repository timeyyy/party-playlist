import os
import queue
import _thread as thread
import subprocess
import time 
from glob import glob
import re
from multiprocessing.pool import ThreadPool
import requests
import string
import unicodedata

import pafy
from pydub import AudioSegment

#~ cvlc -vvv "http://r6---sn-i5onxoxu-q0ne.googlevideo.com/videoplayback?id=3931859f7b57f220&itag=141&source=youtube&mv=m&pl=24&ms=au&mm=31&ratebypass=yes&mime=audio/mp4&gir=yes&clen=5093031&lmt=1381274791935495&dur=213.228&mt=1423698879&upn=MqEfULuo7d0&signature=5CE0FC2B28F1F45FB01F640E81E7C131466CB5F7.86734878E8AE3F9EDE7B317AEEEF26D735E7B5CD&fexp=907263,924637,927622,930016,938648,9405710,9406420,9406555,943917,947225,948124,948703,952302,952605,952612,952901,955301,957201,959701&sver=3&key=dg_yt0&ip=78.48.8.143&ipbits=0&expire=1423720600&sparams=ip,ipbits,expire,id,itag,source,mv,pl,ms,mm,ratebypass,mime,gir,clen,lmt,dur"
#~ cvlc -vvv "http://r3---sn-i5onxoxu-q0nl.googlevideo.com/videoplayback?id=cf086afb3c9a4f85&itag=141&source=youtube&ms=au&pl=23&mv=m&mm=31&ratebypass=yes&mime=audio/mp4&gir=yes&clen=5714575&lmt=1394278914511461&dur=179.211&fexp=900225,907263,912333,927622,933232,9405978,941460,943917,945906,947225,948124,952302,952605,952612,952901,955301,957201,959701&mt=1423697449&sver=3&signature=4313B696B869858D63ACBDE4E3779289468F1AC8.5E601212835696549F8AEFF0926E5D6B6CFFF491&upn=bpqIAmQNwL8&key=dg_yt0&ip=78.48.8.143&ipbits=0&expire=1423719187&sparams=ip,ipbits,expire,id,itag,source,ms,pl,mv,mm,ratebypass,mime,gir,clen,lmt,dur"

class MusicPlayer():
	def __init__(self, *args, **kwargs):
		self.features = ('stream', 'local', 'http', 'all_formats')
		#~ self.output_dir = output_dir
		#~ self.input_dir = input_dir
		self.vlc_start(args, kwargs)
		self.track_queue = queue.Queue()
		self.read_queue()

	def vlc_start(self, *args, **kwargs):
		mode = kwargs.get('mode')
		if mode == 'http':
			pass
			#http setup code here
	def http_play():
		pass
		#start playing
	def http_stop():
		pass
	def http_next():
		pass
	def http_prev():
		pass
	
	def play():pass
				
	def add_track(tracks):
		self.dl()
		self.convert()
		self.track_queue.put(track)
			
	def read_queue(self):
		while 1:
			try:
				track = self.track_queue.get(block=False)
			except queue.Empty:
				pass
			else:	
				print('playing song now!')
				print(track)
				#~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
				subprocess.call(['aplay',track])
				print('Finished playing song ..')
			time.sleep(1)

def test():
	import yaml
	with open("config.conf", 'r') as ymlfile:
		CFG = yaml.load(ymlfile)
	player = MusicPlayer(CFG['aplay']['output_dir'], CFG['aplay']['input_dir'])
		
	yt_api_endpoint = 'https://www.googleapis.com/youtube/v3/'
	yt_key = 'AIzaSyAl1Xq9DwdE_KD4AtPaE4EJl3WZe2zCqg4'
	session = requests.Session()
	def search_youtube(q):
		query = {
		'part': 'id',
		'maxResults': 10,
		'type': 'video',
		'videoCategoryId':'music',
		'q': q,
		'key': yt_key}
		result = session.get(yt_api_endpoint+'search', params=query)
		data = result.json()
		#~ return data
		resolve_pool = ThreadPool(processes=16)
		playlist = [item['id']['videoId'] for item in data['items']]
		#~ return playlist
		playlist = [resolve_url(item) for item in playlist]
		playlist = resolve_pool.map(resolve_url, playlist)
		resolve_pool.close()
		return [item for item in playlist if item]
	
	print(search_youtube('disturbed'))
	
	#~ url = "https://www.youtube.com/watch?v=bMt47wvK6u0"
	#~ video = pafy.new(url)
	#~ print(video.title)
	#~ print(video.rating)
	#~ print(video.viewcount, video.author, video.length)
	#~ print(video.duration, video.likes, video.dislikes)



def add_tracks(tracks):
	self.dl()
	self.convert()
	self.queue.put(track)
		
def convert():
	filenames = []						# Get all files in the cwd		#http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
	for root, dirs, files in os.walk(MUSIC_DIR):	# add to tims tools for listing files...
		root_and_files = [os.path.join(root, file) for file in files]
		filenames.extend(root_and_files)
		break
	
	for file in filenames:
		print("Transcodeing into wav", file)
		try:
			pass
			song = AudioSegment.from_mp3(file)
		except Exception as err:
			print(err)
			print('Problems happend')
			continue
		EXPORT_NAME = file.split(os.sep)[-1]
		#print(EXPORT_NAME)
		song.export(EXPORT_NAME, format="wav")
		#play(EXPORT_NAME)
	
def dummy(self):
	while 1:
		print('Waiting for input!')
		print(self.input_dir)
		for file in glob(self.input_dir+"/*.wav"):
			print('putting on the queue',file)
			self.queue.put(os.path.join(self.input_dir, file))
		time.sleep(2)
	while 1:
		try:
			track = self.track_queue.get(block=False)
		except queue.Empty:
			pass
		else:	
			print('playing song now!')
			print(track)
			#~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
			subprocess.call(['aplay',track])
			print('Finished playing song ..')
		time.sleep(1)

if __name__ == '__main__':		
	test2()
