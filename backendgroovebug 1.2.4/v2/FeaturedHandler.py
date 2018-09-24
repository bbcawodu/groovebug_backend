""" This Handler is responsible for recieving a
    user id in the wrapper of the API call and
    returning a json formatted documents with
    a users home screen info.
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/home?user="""



import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
from google.appengine.api import memcache
from operator import itemgetter, attrgetter
import DataModels as models
import urllib2, urllib, datetime, re, htmlentitydefs, logging
logging.getLogger().setLevel(logging.DEBUG)



""" Section ending with "---" defines class that handles customized user home
    page requests"""
class TilesHandler(webapp.RequestHandler):
    def get(self, user):
# Use GetArtistNews method to obtain news data for given artist
        logging.info('START')
        currentUserId = self.request.get("user")

        finalPreJson = {}
        finalPreJson['status'] = {'error' : '0', 'version' : '2', 'user' : currentUserId}
        finalPreJson['tiles'] = []
        if currentUserId:
            currentUserId = currentUserId.encode('utf-8')
            logging.info('fetching user data from datastore.')
            currentUser = models.GroovebugUser.get_by_key_name(currentUserId)
        else:
            currentUser = None
            
        if currentUser is None:
            finalPreJson['status']['error'] = 'Sorry, user does not exist in database'
        else:
            artistList = currentUser.artistList
            groovebugFavorites = currentUser.groovebugFavorites
                
        logging.info('fetching composite pages')
        Composites = models.CompositePage.all()
        logging.info('composite pages fetched')
        for composite in Composites:
            tile = {}
            tile['name'] = composite.title
            tile['composite'] = composite.compositeUrl
            tile['thumbnail'] = composite.thumbnailUrl
            if composite.status:
                tile['status'] = composite.status
            else:
                tile['status'] = 'Normal'
                
            if currentUser is None:
                tile['match percent'] = 0
                tile['match'] = {}
                tile['match']['library'] = 0
                tile['match']['favorites'] = 0
            else:
                tile['match'] = {}
                if artistList is not None:
                    tile['match']['library'] = str(models.getCompositeScoreNew(composite, artistList))
                else:
                    tile['match']['library'] = 0.0
                if groovebugFavorites is not None:
                    tile['match']['favorites'] = str(models.getCompositeScoreNew(composite, groovebugFavorites))
                else:
                    tile['match']['favorites'] = 0.0
                tile['match percent'] = tile['match']['library']
            finalPreJson['tiles'].append(tile)

        def matchFloat(x): return float(x['match percent']);
        
        sortTiles = sorted(finalPreJson['tiles'], key=matchFloat, reverse=True)
        finalPreJson['tiles'] = sortTiles
        logging.info('FINISH')
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))
""" --- """



""" Main function which handles url mappings"""
application = webapp.WSGIApplication([('/v2/featured(.*)', TilesHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
