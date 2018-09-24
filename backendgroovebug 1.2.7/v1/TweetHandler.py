""" This Handler is responsible for making the API calls to echonest, parsing the
    json data for a given artist, creating our own html document for artist bio
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/bio?artist="""



import os, logging
from os import path
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']

if str(hostUrl) == 'backendgroovebug.appspot.com':
    APIKEY = '269A92REW5YH3KNZW'
elif str(hostUrl) == 'testgroovebug.appspot.com':
    APIKEY = 'GN7EUP6EYOFTT75NN'
else:
    APIKEY = 'GN7EUP6EYOFTT75NN'
    
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
import DataModels as models
from django.utils import simplejson as json
import urllib, urllib2


""" Class that handles Twitter requests"""
class TweetFinder(webapp.RequestHandler):
    def get(self, artist):
## create json data for the given artist
        name = self.request.get("artist")
        qryStr = ''
        retJson = {}
        if name:
            name = name.strip()
            if name == '':
                actionMsg = 'Artist name is missing'
                retJson['error'] = actionMsg
            else:
                nameEnc = name.encode('utf-8')
                retJson['name'] = name
                nameNoSpace = nameEnc.replace(' ', '')
                nameNoSpace = nameNoSpace.lower()
                twitterID = getTwit(nameEnc)
                if twitterID != '':
                    prePop = '@' + twitterID + ' @groovebug'
                    retJson['handle'] = '@' + twitterID
                    twitterID = twitterID.encode('utf-8')
                    retJson['handle widget'] = 'http://' + str(hostUrl) + '/v1/twidgetpr?query=' + urllib.quote(twitterID)
                    if twitterID == nameNoSpace:
                        if nameNoSpace == nameEnc.lower():
                            qryStr = urllib.quote('@' + twitterID + ' OR #' + twitterID + ' OR ' + nameNoSpace)
                        else:
                            qryStr = urllib.quote('@' + twitterID + ' OR #' + twitterID + nameNoSpace + ' OR ("' + nameEnc.lower() + '")')
                        qryStr = 'http://' + str(hostUrl) + '/v1/twidget?query=' + qryStr
                    else:
                        if nameNoSpace == nameEnc.lower():
                            qryStr = urllib.quote('@' + twitterID + ' OR #' + twitterID + ' OR #' + nameNoSpace + ' OR ' + nameNoSpace)
                        else:
                            qryStr = urllib.quote('@' + twitterID + ' OR #' + twitterID + ' OR #' + nameNoSpace + 'OR' + nameNoSpace + ' OR ("' + nameEnc.lower() + '")')
                        qryStr = 'http://' + str(hostUrl) + '/v1/twidget?query=' + qryStr
                else:
                    prePop = '#' + nameNoSpace.decode('utf-8') + ' @groovebug'
                    if nameNoSpace == nameEnc.lower():
                        qryStr = urllib.quote('#' + nameNoSpace + ' OR ' + nameNoSpace)
                    else:
                        qryStr = urllib.quote('#' + nameNoSpace + ' OR ' + nameNoSpace + ' OR ("' + nameEnc.lower() + '")')
                    qryStr = 'http://' + str(hostUrl) + '/v1/twidget?query=' + qryStr

                retJson['prepopulated tweet'] = prePop
                retJson['widget'] = qryStr
                
        else:
            actionMsg = 'Artist name is missing'
            retJson['error'] = actionMsg

        self.response.headers['Content-Type'] = 'application/json'
        #self.response.out.write(retJson)
        self.response.out.write(json.dumps(retJson, separators=(',',':')))        
""" --- """

""" Class that handles Twitter Search requests"""
class TweetHandler(webapp.RequestHandler):
    def get(self, query):
## Use GetArtistMusic method to obtain json data for the given artist
        query = self.request.get("query")
        html = None
        qryStr = ''
        if query:
            #query = query.strip()
            if query == '':
                pass
            else:
                query = query.encode('utf-8')
                qryStr = query

        
## If the echonest API request timed out, display error message
        if html is None:
            if qryStr != '':  
                context = {'searchStr' : qryStr, 'altMsg' : "Searching For Tweets"}
                tmpl = path.join(path.dirname(__file__), 'twitter.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            else:
                context = {'qryStr' : 'from:groovebug OR @groovebug OR #groovebug', 'altMsg' : "Searching For Tweets"}
                tmpl = path.join(path.dirname(__file__), 'twitter.html')
                html = render(tmpl, context)
                self.response.out.write(html)
        else:
            self.response.out.write(html)

""" --- """

""" Class that handles Twitter Profile requests"""
class TweetPrHandler(webapp.RequestHandler):
    def get(self, query):
## Use GetArtistMusic method to obtain json data for the given artist
        query = self.request.get("query")
        html = None
        qryStr = ''
        actionMsg = ''
        if query:
            #query = query.strip()
            if query == '':
                actionMsg = 'Twitter ID is missing'
            else:
                query = query.encode('utf-8')
                qryStr = query
                
        else:
            actionMsg = 'Twitter ID is missing'
        
## If the echonest API request timed out, display error message
        if html is None:
            if qryStr != '':
                context = {'twitterID' : qryStr, 'altMsg' : "Searching For Tweets"}
                tmpl = path.join(path.dirname(__file__), 'twitterpr.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            else:
                actionMsg = 'Twitter ID is missing'
                self.response.out.write(actionMsg)
        else:
            if actionMsg == '':
                self.response.out.write(html)
            else:
                self.response.out.write(actionMsg)

""" --- """


def getTwit(artist):
    artistEnc = urllib.quote_plus(artist)
    socialFile = models.ArtistSocial.gql("WHERE artistName = :1 LIMIT 1", artistEnc).fetch(1)

    if len(socialFile) > 0:
        if socialFile[0].twitter:
            if socialFile[0].twitter != '':
                return socialFile[0].twitter
    else:
        socialFile = models.ArtistSocial.get_or_insert(key_name = str(artistEnc), artistName = artistEnc)

    twitterID = ''
    searchBase = 'http://groovebug.api3.nextbigsound.com/artists/search.json?q=' + artistEnc
    echoBase = 'http://developer.echonest.com/api/v4/artist/twitter?api_key=' + APIKEY + '&format=json&name=' + artistEnc  
    try:
        echoNestJson = json.load(urllib2.urlopen(echoBase))
        if echoNestJson.has_key('response'):
            echoResults = echoNestJson['response']
            if echoResults.has_key('artist'):
                echoArtist = echoResults['artist']
                if echoArtist.has_key('twitter'):
                    twitterID = echoArtist['twitter']
                    logging.info('The twitter ID ' + twitterID.encode('utf-8') + ' was found on EchoNest')
                    socialFile.twitter = twitterID
                    socialFile.put()
                    
        artistIDJson = json.load(urllib2.urlopen(searchBase))
        #return artistIDJson
        if (artistIDJson.has_key('status')):
            return twitterID
            
        def bystars(k):
            return int(artistIDJson[k]['stars'])
        sortedArtistIDJson = sorted(artistIDJson, key=bystars, reverse=True)

        nbsIndex = 0
        testBound = 3
        if len(sortedArtistIDJson) > 1: 
            if len(sortedArtistIDJson) > testBound:
                endloop = testBound - 1
            else:
                endloop = len(sortedArtistIDJson) - 1

            for i in range(0, endloop):
                jKey = sortedArtistIDJson[i]
                if artist.lower() == artistIDJson[jKey]['name'].lower():
                    nbsIndex = i  
                    break

        nbsID = sortedArtistIDJson[nbsIndex]
        
        searchBase = 'http://groovebug.api3.nextbigsound.com/profiles/artist/'+ str(nbsID) + '.json'
        artistProfilesJson = json.load(urllib2.urlopen(searchBase))
        artistProfilesJsonKeys = artistProfilesJson.keys()
        for k in artistProfilesJsonKeys:
            if artistProfilesJson[k]['name'] == "Twitter":
                if twitterID == '':
                    twitterUrl = artistProfilesJson[k]['url']
                    twitterUrl = twitterUrl.strip()
                    begCut = twitterUrl.find('http://twitter.com/')
                    if begCut >= 0:
                        twitterID = twitterUrl[begCut+19: ]
                        twitterID = twitterID.strip()
                        twitterID = twitterID.replace('/', '')
                        socialFile.twitter = twitterID
                        #socialFile.put()
            elif artistProfilesJson[k]['name'] == "Facebook":
                facebookUrl = artistProfilesJson[k]['url']
                facebookUrl = facebookUrl.strip()
                socialFile.facebook = facebookUrl
                #socialFile.put()
            elif artistProfilesJson[k]['name'] == "MySpace":
                myspaceUrl = artistProfilesJson[k]['url']
                myspaceUrl = myspaceUrl.strip()
                socialFile.myspace = myspaceUrl
                #socialFile.put()
            elif artistProfilesJson[k]['name'] == "SoundCloud":
                soundcloudUrl = artistProfilesJson[k]['url']
                soundcloudUrl = soundcloudUrl.strip()
                socialFile.soundcloud = soundcloudUrl
            elif artistProfilesJson[k]['name'] == "Wikipedia":
                wikipediaUrl = artistProfilesJson[k]['url']
                wikipediaUrl = wikipediaUrl.strip()
                socialFile.wikipedia = wikipediaUrl
            elif artistProfilesJson[k]['name'] == "YouTube":
                youtubeUrl = artistProfilesJson[k]['url']
                youtubeUrl = youtubeUrl.strip()
                socialFile.youtube = youtubeUrl
            elif artistProfilesJson[k]['name'] == "Last.fm":
                lastfmUrl = artistProfilesJson[k]['url']
                lastfmUrl = lastfmUrl.strip()
                socialFile.lastfm = lastfmUrl
            elif artistProfilesJson[k]['name'] == "Purevolume":
                purevolumeUrl = artistProfilesJson[k]['url']
                purevolumeUrl = purevolumeUrl.strip()
                socialFile.purevolume = purevolumeUrl
        socialFile.put()
        
        return twitterID
    except Exception, error:
        logging.debug(error)
        return ''
        #return 'try error - ' + str(error)

""" Section ending with "---" defines code that handles exceptions when making urlfetch requests"""
def RetryUrlFetch(url, counter = 0, maxTries = 3):
    try:
        loadedFetch = urlfetch.Fetch(url)
    except urlfetch.Error:
        if counter < maxTries:
            counter += 1
            return RetryUrlFetch(url, counter)
        else:
            return []
    return loadedFetch

""" --- """

""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/twitter(.*)', TweetFinder),
                                      ('/v1/twidgetpr(.*)', TweetPrHandler),
                                      ('/v1/twidget(.*)', TweetHandler),],
                                       debug=True)
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
