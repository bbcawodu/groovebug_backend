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
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
import DataModels as models
from django.utils import simplejson as json
import urllib, urllib2
from operator import itemgetter, attrgetter


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
                    retJson['handle widget'] = 'http://' + str(hostUrl) + '/v1/twidget?query=' + urllib.quote_plus('from:' + twitterID)
                    if twitterID == nameNoSpace:
                        if nameNoSpace == nameEnc.lower():
                            qryStr = urllib.quote_plus('@' + twitterID + ' OR #' + twitterID + ' OR ' + nameNoSpace)
                        else:
                            qryStr = urllib.quote_plus('@' + twitterID + ' OR #' + twitterID + nameNoSpace + ' OR (' + nameEnc.lower() + ')')
                        qryStr = 'http://' + str(hostUrl) + '/v1/twidget?query=' + qryStr
                    else:
                        if nameNoSpace == nameEnc.lower():
                            qryStr = urllib.quote_plus('@' + twitterID + ' OR #' + twitterID + ' OR #' + nameNoSpace + ' OR ' + nameNoSpace)
                        else:
                            qryStr = urllib.quote_plus('@' + twitterID + ' OR #' + twitterID + ' OR #' + nameNoSpace + 'OR' + nameNoSpace + ' OR (' + nameEnc.lower() + ')')
                        qryStr = 'http://' + str(hostUrl) + '/v1/twidget?query=' + qryStr
                else:
                    prePop = '#' + nameNoSpace.decode('utf-8') + ' @groovebug'
                    if nameNoSpace == nameEnc.lower():
                        qryStr = urllib.quote_plus('#' + nameNoSpace + ' OR ' + nameNoSpace)
                    else:
                        qryStr = urllib.quote_plus('#' + nameNoSpace + ' OR ' + nameNoSpace + ' OR (' + nameEnc.lower() + ')')
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

""" Class that handles Twitter requests"""
class TweetHandler(webapp.RequestHandler):
    def get(self, query):
## Use GetArtistMusic method to obtain json data for the given artist
        query = self.request.get("query")
        html = None
        qryStr = ''
        actionMsg = ''
        if query:
            #query = query.strip()
            if query == '':
                actionMsg = 'Query string is missing'
            else:
                query = query.encode('utf-8')
                qryStr = query
                #nameNoSpace = name.replace(' ', '')
                #nameNoSpace = nameNoSpace.lower()
                
        else:
            actionMsg = 'Query string is missing'
            #retJson['error'] = actionMsg
        
## If the echonest API request timed out, display error message
        if html is None:
            if qryStr != '':
                context = {'searchStr' : qryStr}
                tmpl = path.join(path.dirname(__file__), 'twitter.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            else:
                context = {'qryStr' : 'from:groovebug OR @groovebug OR #groovebug'}
                tmpl = path.join(path.dirname(__file__), 'twitter.html')
                html = render(tmpl, context)
                self.response.out.write(html)
        else:
            self.response.out.write(html)

""" --- """

def getTwit(artist):
    artistEnc = urllib.quote_plus(artist)
    socialFile = models.ArtistSocial.gql("WHERE artistName = :1 LIMIT 1", artistEnc).fetch(1)
    if len(socialFile) > 0:
        if socialFile[0].twitter:
            if socialFile[0].twitter != '':
                return socialFile[0].twitter

    twitterID = ''
    searchBase = 'http://groovebug.api3.nextbigsound.com/artists/search.json?q=' + artistEnc  
    try:
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

        if not(len(socialFile) > 0):
            socialFile = models.ArtistSocial.get_or_insert(key_name = str(artistEnc), artistName = artistEnc)
        
        searchBase = 'http://groovebug.api3.nextbigsound.com/profiles/artist/'+ str(nbsID) + '.json'
        artistProfilesJson = json.load(urllib2.urlopen(searchBase))
        artistProfilesJsonKeys = artistProfilesJson.keys()
        for k in artistProfilesJsonKeys:
            if artistProfilesJson[k]['name'] == "Twitter":
                twitterUrl = artistProfilesJson[k]['url']
                twitterUrl = twitterUrl.strip()
                begCut = twitterUrl.find('http://twitter.com/')
                if begCut >= 0:
                    twitterID = twitterUrl[begCut+19: ]
                    twitterID = twitterID.strip()
                    twitterID = twitterID.replace('/', '')
                    socialFile.twitter = twitterID
                    socialFile.put()
            elif artistProfilesJson[k]['name'] == "Facebook":
                facebookUrl = artistProfilesJson[k]['url']
                facebookUrl = facebookUrl.strip()
                socialFile.facebook = facebookUrl
                socialFile.put()
                #begCut = facebookUrl.find('http://www.facebook.com/')
                #if begCut >= 0:
                #    facebookID = facebookUrl[begCut+24: ]
                #    facebookID = facebookID.strip()
                #    facebookID = facebookID.replace('/', '')
                #    socialFile.facebook = facebookID
                #    socialFile.put()
            elif artistProfilesJson[k]['name'] == "MySpace":
                myspaceUrl = artistProfilesJson[k]['url']
                myspaceUrl = myspaceUrl.strip()
                socialFile.myspace = myspaceUrl
                socialFile.put()
                #begCut = myspaceUrl.find('http://www.myspace.com/')
                #if begCut >= 0:
                #    myspaceID = myspaceUrl[begCut+23: ]
                #    myspaceID = myspaceID.replace('/', '')
                #    socialFile.myspace = myspaceID
                #    socialFile.put()


        
        return twitterID
    except Exception, error:
        logging.debug(error)
        return ''
        #return 'try error - ' + str(error)



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/twitter(.*)', TweetFinder),
                                      ('/v1/twidget(.*)', TweetHandler),],
                                       debug=True)
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
