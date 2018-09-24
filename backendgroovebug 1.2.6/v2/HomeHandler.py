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



class HomeHandler(webapp.RequestHandler):
    """ Class that handles requests for data for the groovebug home screen. The
        handler requires a groovebug user ID as a 'user' parameter. If the request
        containins a POST with a JSON document with a users library data, the
        handler generates library mappings and retrieves mapping data from datastore
        if there is no post."""
    def get(self, user):
        logging.info('START GET')
        currentUserId = self.request.get("user")

## Use DataModels method GetSavedUserData to fetch users library and favorites information if there is a UDID in the request and
## produce an error within the JSON if no UDID in request
        if currentUserId:
            currentUserId = currentUserId.encode('utf-8')
            if self.request.get('fbauth'):
                fbAuth = self.request.get('fbauth')
                libraryData = models.GetSavedUserData(currentUserId, fbAuth = fbAuth)
            else:
                libraryData = models.GetSavedUserData(currentUserId)
            logging.info('FINISH')
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps(libraryData, separators=(',',':')))
        else:
            finalPreJson = {}
            finalPreJson['status'] = {'error' : 'No UDID in url', 'version' : '2'}
            logging.info('FINISH')
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))
            
    def post(self, user):
        logging.info('START POST')
        loadedJson = json.load(self.request.body_file)
        currentUserId = self.request.get("user")

## Use DataModels method GetVerifiedData to correct users library vs echonest and map the library/favorites to said
## correctionsif there is a UDID in the request and produce an error within the JSON if no UDID in request
        if currentUserId:
            currentUserId = currentUserId.encode('utf-8')
            if self.request.get('fbauth'):
                fbAuth = self.request.get('fbauth')
                verifiedLibraryData = models.GetVerifiedData(loadedJson, currentUserId, fbAuth = fbAuth)
            else:
                verifiedLibraryData = models.GetVerifiedData(loadedJson, currentUserId)
            logging.info('FINISH')
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps(verifiedLibraryData, separators=(',',':')))
        else:
            finalPreJson = {}
            finalPreJson['status'] = {'error' : 'No UDID in url', 'version' : '2'}
            logging.info('FINISH')
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps(finalPreJson, separators=(',',':')))



""" Main function which handles url mappings"""
application = webapp.WSGIApplication([('/v2/home(.*)', HomeHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
