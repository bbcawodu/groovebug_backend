""" This Handler is responsible for making the API calls to youtube, parsing the
    json data for a given artist, creating a formatted HTML document with youtube
    video links, and returning it when queried using our internal API
    the wrapper for videos will be
    http://backendgroovebug.appspot.com/v1/videos?artist="""



import os
from os import path
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import DataModels as models
import urllib2, urllib



""" This function recieves an artist name as an input and outputs an array of dictionaries
    which contain a title, video link, and thumbnail link. There is an optional second
    argument for the max amount of entries in the array, default is 20."""
def GetArtistVideos(artist, maxResults = 20):
## Encode results into unicode which can be parsed by iTunes API
    artist = artist.encode('utf-8')
    artistName = urllib.quote_plus(artist)
## Initialize list that will contain dictionary entries with video data
    videos = []
    ExclList = []
    PromoList = []
    PromoSetList = []
    VidRec = db.GqlQuery("SELECT * FROM ArtistVideos WHERE artistName = :1 LIMIT 1",
                           artistName).fetch(1)
    if len(VidRec) > 0:
        ExclList = VidRec[0].videosToExclude
        PromoList = VidRec[0].videosToPromote
        #return PromoList
        if ExclList:
            if len(ExclList) > 0:
                maxResults = maxResults + len(ExclList)
                if maxResults > 50:
                    maxResults = 50
        else:
            ExclList = []

        PromoSetList = []
        if PromoList:
            if len(PromoList) > 0:
                for entry in PromoList:
                    PromoSetList.append(entry['link'])
            else:
                PromoList = []
            
    ExclSet = set(ExclList)
    PromoSet = set(PromoSetList)

## Populate videos list with promo videos dictionary entries with "title", "thumbnail", and video link data           
    for entry in PromoList:
        #entryJson = json.loads(entry)
        if entry['link'] not in ExclSet:
            video = {}
            video['title'] = entry['title']
            video['thumb'] = entry['thumb']
            video['link'] = entry['link']
            tempLink = entry['link'] + '&title=' + urllib.quote(entry['title'].encode('utf-8'))
            video['fulllink'] = tempLink
            video['promoted'] = True
            videos.append(video)
    
## Obtain Json text for specified artist from youtube
    searchBase = 'http://gdata.youtube.com/feeds/api/videos?'
    searchArgs = {'alt' : 'json',
                  'q' : "\"" + artist + "\"",
                  'key' : 'AI39si4valAWDvFNMsZCFKWydGjC9yMHhMmSvQ_lHINbx8dA1oWUinsFSLfRoBc7ojrynjN65ZBqogEjStplkSPfPfvQ-1n_rw',
                  'max-results' : maxResults,
                  'category' : 'Music',
                  'format' : '6',}
    url = str(searchBase) + urllib.urlencode(searchArgs)
    
# Try loading Json doc from URL, if loading times out, try again up to
# 'maxLookupRetry' times
    artistJson = models.RetryLoadJson(url)
    if artistJson == []:
        errorMessage = 'The YouTube API request timed out'
        return errorMessage
    
    videoJson = artistJson['feed']

## Returns empty videos list if videos for artist are not found on youtube 
    if not videoJson.has_key('entry'):
        return videos

            
## Populate videos list with dictionary entries with "title", "thumbnail", and video link data
    artistDict = videoJson['entry']
            
    for entry in artistDict:
        if entry['link'][0]['href'] not in ExclSet and entry['link'][0]['href'] not in PromoSet:
            video = {}
            video['title'] = entry['title']['$t']
            video['thumb'] = entry['media$group']['media$thumbnail'][0]['url']
            video['link'] = entry['link'][0]['href']
            tempLink = entry['link'][0]['href'] + '&title=' + urllib.quote(entry['title']['$t'].encode('utf-8'))
            video['fulllink'] = tempLink
            video['promoted'] = False
            videos.append(video)

## Return populated videos list
    return videos



""" Class that handles video requests"""
class VideoHandler(webapp.RequestHandler):
    def get(self, artist):
## Use GetArtistVideos method to obtain video data from youtube
        videos = GetArtistVideos(self.request.get("artist"))

## If the Youtube API request timed out, display error message
        if videos == 'The YouTube API request timed out':
            context = {'error' : 'The YouTube API request timed out'}
            tmpl = path.join(path.dirname(__file__), 'video.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# If there are no videos found on youtube for the artist, display error message
        elif not videos:
            context = {'error' : 'Sorry, there are no videos found on youtube for this artist'}
            tmpl = path.join(path.dirname(__file__), 'video.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# Otherwise, use video data to create html document
        else:
            context = {'videos' : videos}
            tmpl = path.join(path.dirname(__file__), 'video.html')
            html = render(tmpl, context)
            self.response.out.write(html)
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/videos(.*)', VideoHandler),],
                                     debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
