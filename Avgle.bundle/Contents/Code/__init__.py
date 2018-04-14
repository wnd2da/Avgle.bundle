# -*- coding: UTF-8 -*-
import re
import urllib2
import json
import ssl

def Start():
	pass

class AvgleAgent(Agent.Movies):
	name = 'Avgle.com'
	languages = [Locale.Language.English, Locale.Language.Korean, Locale.Language.Japanese]
	primary_provider = True
	accepts_from = ['com.plexapp.agents.localmedia']
	contributes_to = ['com.plexapp.agents.imdb','com.plexapp.agents.data18']

	def search(self, results, media, lang, manual):
		Log('media.name:%s' % media.name)
		Log('lang:%s' % lang)
		Log('manual:%s' % manual)
		query = media.name.replace(' ', '-')
		url = 'https://api.avgle.com/v1/jav/%s/0?limit=10' % query
		Log('SEARCH URL:%s' % url)
		request = urllib2.Request(url)
		response = urllib2.urlopen(request, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
		data = json.load(response, encoding="utf-8")
		Log('SEARCH DATA:%s' % data)
		if data['success']:
			videos = data['response']['videos']
			for idx in range(0, len(videos)):
				video = videos[idx]
				id = video['vid']
				name = video['title']
				#name = translate(name)
				name = titleChange(name)
				year = media.year
				score = 100 - (idx*5)
				new_result = dict(id=id, name=name, year='', score=score, lang=lang)
				results.Append(MetadataSearchResult(**new_result))

	def update(self, metadata, media, lang):
		Log('update metadata.id:%s' % metadata.id)
		vid = metadata.id
		url = 'https://api.avgle.com/v1/video/%s' % vid
		request = urllib2.Request(url)
		response = urllib2.urlopen(request, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
		data = json.load(response, encoding="utf-8")
		Log('UPDATE DATA:%s' % data)
		if data['success']:
			video = data['response']['video']
			name = video['title']
			name = translate(name)
			name = titleChange(name)
			metadata.title = name
			metadata.tagline = translate(video['keyword'])
			str = name + '\n'
			str += 'Keyword : %s\n' % metadata.tagline
			str += video['embedded_url'] + '\n'
			str += video['preview_url'] + '\n'
			metadata.summary = str
			poster_url = video['preview_url']
			try:
				#for mode in ['left', 'right']:
				if Prefs['POSTER_SPLIT_PAGE_URL'] == '' or Prefs['POSTER_SPLIT_PAGE_URL'] is None: raise
				for mode in ['right']:
					tmp = '%s?mode=%s&url=%s' % (Prefs['POSTER_SPLIT_PAGE_URL'], mode, poster_url)
					poster = HTTP.Request( tmp )
					try: metadata.posters[tmp] = Proxy.Media(poster)
					except: pass
			except Exception as e:
				poster = HTTP.Request( poster_url )
				try: metadata.posters[poster_url] = Proxy.Media(poster)
				except: pass

def translate(str):
	try:
		client_id = Prefs['PAPAGO_CLIENT_ID']
		client_secret = Prefs['PAPAGO_CLIENT_SECRET']
		if client_id == '' or client_id is None or client_secret == '' or client_secret is None: return
		encText = str
		data = "source=ja&target=ko&text=" + encText
		url = "https://openapi.naver.com/v1/papago/n2mt"
		requesturl = urllib2.Request(url)
		requesturl.add_header("X-Naver-Client-Id", client_id)
		requesturl.add_header("X-Naver-Client-Secret", client_secret)
		response = urllib2.urlopen(requesturl, data = data.encode("utf-8"), context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
		#response = urllib2.urlopen(requesturl, data = data.encode("utf-8"))
		data = json.load(response, encoding="utf-8")
		Log(data)
		rescode = response.getcode()
		if rescode == 200:
			return data['message']['result']['translatedText']
		else:
			return str
	except Exception as e:
		Log('XXXXX %s' % e)
		return str

def titleChange(str):
	p = re.compile('[a-zA-Z]+-\d+')
	m = p.search(str)
	if m:
		name = m.group()
		ret = str.replace(name, '').strip()
		ret = '[%s] %s' % (name, ret)
		return ret
	else:
		return str
