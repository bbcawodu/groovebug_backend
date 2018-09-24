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
class HomeHandler(webapp.RequestHandler):
    def get(self, user):
        logging.info('START')
        currentUserId = self.request.get("user")

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
# Use GetArtistNews method to obtain news data for given artist
        logging.info('START')
        loadedJson = json.load(self.request.body_file)
        currentUserId = self.request.get("user")

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
""" --- """



""" Main function which handles url mappings"""
application = webapp.WSGIApplication([('/v2/home(.*)', HomeHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
