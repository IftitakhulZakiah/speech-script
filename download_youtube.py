# from pytube import YouTube
# import os
from __future__ import unicode_literals
import youtube_dl


urls=['https://www.youtube.com/watch?v=3dtTl6huIQ4',
	'https://www.youtube.com/watch?v=DSJnlZQ651A']


def downloadYoutube(vid_url, path):
	yt = YouTube(vid_url)
	yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
	# if not os.path.exists(path):
	# 	os.makedirs(path)

if __name__ == '__main__':
	# for url in urls:
	# 	youtube = pytube.Youtube(url)
	# 	video = youtube.streams.first()
	# 	video.download('/srv/data1/speech/public/menlu/master/RM/')

		# downloadYoutube(url, path)

	ydl_opts = {
	    # 'format': 'bestaudio/best',
	    # 'postprocessors': [{
	    #     'key': 'FFmpegExtractAudio',
	    #     'preferredcodec': 'wav',
	    #     'preferredquality': '192',
	    # }],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    ydl.download(urls)