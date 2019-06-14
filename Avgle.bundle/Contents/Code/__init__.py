# -*- coding: UTF-8 -*-
import os
import re
import urllib
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
        query = media.name.lower()
        query = query.replace(' ', '')
        query = query.replace('fc2ppv', '').strip()
        match = Regex(r'(?P<cd>cd\d{1,2})$').search(query)
        if match:
            query = query.replace(match.group('cd'), '')

        url = '%s/jav_agent/avgle/search?arg=%s' % (Prefs['SJVA_SERVER'], query)
        data = JSON.ObjectFromURL(encoding='utf-8', url=url)
        Log('SEARCH DATA:%s' % data)
        if data['success']:
            videos = data['response']['videos']
            for idx in range(0, len(videos)):
                video = videos[idx]
                id = video['vid']
                name = video['title']
                name = titleChange(name)
                year = media.year
                score = 100 - (idx*5)
                new_result = dict(id=id, name=name, year=year, score=score, lang=lang)
                results.Append(MetadataSearchResult(**new_result))

    def update(self, metadata, media, lang):
        Log('update metadata.id:%s' % metadata.id)
        Log(media)
        vid = metadata.id
        url = '%s/jav_agent/avgle/update?arg=%s' % (Prefs['SJVA_SERVER'], vid)
        data = JSON.ObjectFromURL(encoding='utf-8', url=url)

        Log('UPDATE DATA:%s' % data)
        if data['success']:
            video = data['response']['video']
            name = video['title']
            name = translate(name)
            name = change_html(name)
            parts = media.all_parts()
            filename = parts[0].file
            search_name = os.path.basename(filename).split('.')[0]#.replace('-', ' ')
            #search_name = search_name.split(' ')[0]
            #metadata.title = '[%s] %s' % (search_name, name)
            metadata.title = '%s' % (name)
            metadata.tagline = translate(video['keyword'])
            str = name + '\n'
            str += 'Keyword : %s\n' % metadata.tagline
            str += video['embedded_url'] + '\n'
            str += video['preview_url'] + '\n'
            metadata.summary = str
            poster_url = video['preview_url']
            try:
                if Prefs['SJVA_SERVER'] == '' or Prefs['SJVA_SERVER'] is None: raise
                tmp = '%s/jav_agent/image_rotate?rotate=90&image_url=%s' % (Prefs['SJVA_SERVER'], poster_url)
                poster = HTTP.Request( tmp )
                try: metadata.posters[tmp] = Proxy.Media(poster)
                except: pass
            except Exception as e:
                poster = HTTP.Request( poster_url )
                try: metadata.posters[poster_url] = Proxy.Media(poster)
                except: pass


def translate(text):
    try:
        if Prefs['SJVA_SERVER'] == '' or Prefs['SJVA_SERVER'] is None:
            return text
        url = "%s/jav_agent/trans" % (Prefs['SJVA_SERVER'])
        Log(url)
        data = {'text':text, 'source':'ja', 'target':'ko'}
        data = urllib.urlencode(data)
        requesturl = urllib2.Request(url, data=data)
        response = urllib2.urlopen(requesturl)
        j = json.loads(response.read())
        return j['ret']
    except Exception as e:
        Log('XXXXX %s' % e)
        return text

def titleChange(str):
    p = re.compile(r'[a-zA-Z]+-\d+')
    m = p.search(str)
    if m:
        name = m.group()
        ret = str.replace(name, '').strip()
        ret = '[%s] %s' % (name, ret)
        return ret
    else:
        return str

def change_html(str):
    return str.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"').replace('&#35;', '#').replace('&#39;', "‘")