""" This handler is responsible for creating Json document with links
    to our own internal API links for the other handlers for the app
    http://backendgroovebug.appspot.com/v1/magazine?artist=&user="""



import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import urllib2, urllib, datetime
import DataModels as models
 


""" Class that handles magazine requests"""
class MagazineHandler(webapp.RequestHandler):
    def get(self, artist):
        if self.request.get('user'):
            userId = self.request.get('user')
            currentUser = models.GroovebugUser.get_by_key_name(userId.encode('utf-8'))
            if currentUser is None:
                currentUser = models.GroovebugUser(key_name = userId.encode('utf-8'), userId = userId.encode('utf-8'), visitedSites = self.request.url.encode('utf-8'))
                currentUser.put()
            else:
                currentUser.visitedSites = currentUser.visitedSites + self.request.url.encode('utf-8') + '\n'
                currentUser.put()
            magazineJson = models.GetArtistMagazine(self.request.get("artist"), userId)
            
## Use GetArtistMagazine method to obtain json data for the given artist
        else:
            magazineJson = models.GetArtistMagazine(self.request.get("artist"))

## Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(magazineJson)
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/magazine(.*)', MagazineHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
