""" This Handler is responsible for making the API calls to echonest, parsing the
    json data for a given artist, creating our own json formatted dictionary of
    similar artist info, and returning it when queried using our internal API
    the wrapper for similar artists will be
    http://backendgroovebug.appspot.com/v1/similar?artist="""


from __future__ import with_statement
import os
from os import path
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import urllib2, urllib, datetime
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api import urlfetch, apiproxy_stub_map
from google.appengine.api import files
import DataModels as models
import echonestlib as echonest

if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']


""" This section of code which ends with a "---" block defines the method that recieves
    an artist name as an input and outputs a json formatted dictionary of similar artist
    info"""
def GetSimilarArtist(artist, minPics = 3):
# Encode results into unicode which can be parsed by Echonest API
##    artist = artist.encode('utf-8')

    simData = memcache.get(artist + ' Similar')
    if simData is not None:
        missingURL = 'http://' + str(hostUrl) + '/htmlimages/missing_profile_icon.png'
        missingFound = False
        simJsonData = json.loads(simData)
        for entry in simJsonData['artists']:
            if entry['thumbnail'] == missingURL:
                missingFound = True
                break
            
        if not missingFound:    
            return simData

# Initiallize the dictionary that will eventually be converted to json
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0'}
    finalPreJson['artists'] = []

# Perform lookup of similar artists for given artist
    similarArtistList = echonest.GetSimilarArtist(artist, maxSimilar = 10)

# Return blank arrays for everything if artist isnt found
    if similarArtistList == []:
        finalPreJson['status']['error'] = 'artists not found'
        finalJson = json.dumps(finalPreJson, separators=(',',':'))
        return finalJson

# for all artists that don't have images call the backgrounds handler
    entryCnt = 0
    backCallCnt = 0
    rpcs = []
    
    for artist in similarArtistList:
        imgRetUrl = getThumb(artist)
        if imgRetUrl == None:
            simArtist = artist
            simArtist = simArtist.encode('utf-8')
            simArtist = urllib.quote_plus(simArtist)
            rpc = urlfetch.create_rpc()
            strCallBackgrounds = 'http://' + str(hostUrl) + '/v1/backgrounds?artist=' + simArtist
            urlfetch.make_fetch_call(rpc, strCallBackgrounds)
            rpcs.append(rpc)
            backCallCnt = backCallCnt + 1

        entryCnt = entryCnt + 1

    if len(rpcs) > 0:
        for rpc in rpcs:
            rpc.wait()

        for i, rpc in enumerate(rpcs):
            try:
                result = rpc.get_result()
                if result.status_code == 200:
                    text = result.content
                    # ...
            except urlfetch.DownloadError:
                # Request timed out or failed.
                # ...
                imgUrlRslt = ''
            
# Insert similar artists into dictionary set to be returned    
    for artist in similarArtistList:
        artistEntry = {}
        
        name = artist
        artistEntry['name'] = name
        artistEntry['magazine'] = 'http://' + str(hostUrl) + '/v1/magazine?artist=' + urllib.quote_plus(name.encode('utf-8'))
        imgRetUrl = getThumb(artist)
        if imgRetUrl == None:
            imgRetUrl = 'http://' + str(hostUrl) + '/htmlimages/missing_profile_icon.png'

        artistEntry['thumbnail'] = imgRetUrl
        finalPreJson['artists'].append(artistEntry)

# Encode final dictionary into json and return it
    finalJson = json.dumps(finalPreJson)
    SetSimilarMemcache(artist, finalJson)
    return finalJson

""" --- """

""" Section ending with "---" defines checks to see if an thumbnail exists for the artist requested"""
def getThumb(artistName):
    artistName = artistName.encode('utf-8')
    artistName = urllib.quote_plus(artistName)

    result = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 1",
      artistName).fetch(1)

    if (len(result) > 0):
        return result[0].artistThmbUrl
    else:
        return None
""" --- """ 



""" Section ending with "---" defines checks to see how many images are already there for an artist"""
def chkImgCnt(artist, cntLimit = 3):

    result = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 1",
      artist).fetch(cntLimit)

    return len(result)
""" --- """



def SetSimilarMemcache(artistName, similarJson):
    simData = memcache.get(artistName + ' Similar')
    if simData is not None:
        memcache.set(artistName + ' Similar', similarJson, 604800)
    else:
        memcache.add(artistName + ' Similar', similarJson, 604800)


        
""" Section ending with "---" defines class that handles similar artist requests"""
class SimilarHandler(webapp.RequestHandler):
    def get(self, artist):
# Use GetArtistMagazine method to obtain json data for the given artist
        magazineJson = GetSimilarArtist(self.request.get("artist"))

# Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(magazineJson)
""" --- """



# URL to source file mappings
application = webapp.WSGIApplication([('/v1/similar(.*)', SimilarHandler),],
                                       debug=True)



""" Main function which handles url mapping"""
def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
""" --- """
