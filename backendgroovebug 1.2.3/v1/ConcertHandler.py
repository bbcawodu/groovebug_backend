""" This Handler is responsible for making the API calls, parsing the
    json data for a given artist, creating our own html document for the news
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/news?artist="""



import os
from os import path
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from operator import itemgetter, attrgetter
from django.utils import simplejson as json
import urllib2, urllib, datetime, re
import DataModels as models

def GetArtistConcerts(artist, maxResults = 8):
# Encode results into unicode which can be parsed by API
    uArtist = artist.encode('utf-8')
    artist = urllib.quote(uArtist)

# Create blank dictionary that will contain news results and info
# about the search
    artistConcerts = {}
    artistConcerts['status'] = {'error' : '0', 'version' : '1.0'}
    artistConcerts['concerts'] = []

# Obtain bandsintown concert items
    searchBase = 'http://api.bandsintown.com/artists/' + artist + '/events.json?app_id=grvbg'
    concertJson = []
    try:
        concertJson = json.load(urllib2.urlopen(searchBase))
    except Exception:
        concertJson = []
        artistConcerts['status']['error'] = 'artist not found'
        
    concertJson = json.load(urllib2.urlopen(searchBase))
    #return concertJson
        
    if concertJson != []:
        if concertJson[0].has_key('errors'):
            if concertJson['errors'] == 'Unknown Artist':
                artistConcerts['status']['error'] = 'artist not found'
        else:
            artistConcerts['concerts'] = concertJson

    if len(artistConcerts['concerts']) > 1:
        sortedArtistConcerts = sorted(artistConcerts['concerts'], key=itemgetter('datetime'), reverse=True)
        artistConcerts['concerts'] = sortedArtistConcerts


    #data = memcache.get(artist + ' Concerts')
    #if data is not None:
    #    memcache.set(artist + ' Concerts', artistConcerts, 10800)
    #else:
    #    memcache.add(artist + ' Concerts', artistConcerts, 10800)
    
    return artistConcerts
""" --- """


""" This class handles news requests"""
class ConcertHandler(webapp.RequestHandler):
    def get(self, artist):
# Use GetArtistNews method to obtain news data for given artist
        name = self.request.get("artist")
        finalPreJson = {}
        finalPreJson['status'] = {'error' : '0', 'version' : '1.0'}
        finalPreJson['concerts'] = []
        
        concertData = None
        #if name:
        #    html = memcache.get(name + ' Concerts')
        #    if html is None:
        #        concertData = GetArtistConcerts(name)
        #else:
        #    concertData = {'status' : {'error' : 'artist unknown'}}

        concertData = GetArtistConcerts(name)
        #self.response.headers['Content-Type'] = "application/json"
        #self.response.out.write(concertData)
        #self.response.out.write(json.dumps(concertData, separators=(',',':')))
        #return 'ok'
        if concertData is None:
            if concertData['status']['errors'] == 'The API call timed out':
                finalPreJson['status']['error'] = concertData['status']['errors']
                self.response.headers['Content-Type'] = "application/json"
                self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))
            elif concertData['status']['errors'] != '0':
                finalPreJson['status']['error'] = concertData['status']['errors']
                self.response.headers['Content-Type'] = "application/json"
                self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))
            elif concertData['concerts'] == []:
                finalPreJson['status']['error'] = 'There are no concerts for this artist'
                self.response.headers['Content-Type'] = "application/json"
                self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))
            else:
                finalPreJson['concerts'] = concertData['concerts']
                self.response.headers['Content-Type'] = "application/json"
                self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))
        else:
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps(concertData, separators=(',',':')))
""" --- """

def SetNewsMemcache(artistName, newsHTML):
    data = memcache.get(artistName + ' News')
    if data is not None:
        memcache.set(artistName + ' News', newsHTML, 10800)
    else:
        memcache.add(artistName + ' News', newsHTML, 10800)
        

""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/concerts(.*)', ConcertHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
