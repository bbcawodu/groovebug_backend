""" This Handler is responsible for recieving a POST of a
    list of locally stored artists and returning a Json
    formatted document of the verified artists
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/verify?user="""



import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import DataModels as models
import urllib, logging
logging.getLogger().setLevel(logging.DEBUG)

    
""" Class that handles verification requests"""
class VerificationHandler(webapp.RequestHandler):
    def post(self, user):
        loadedJson = json.load(self.request.body_file)
        currentUserId = self.request.get("user")
        currentUserId = currentUserId.encode('utf-8')
        if self.request.get('fbid') and self.request.get('fbauth'):
            fbID = self.request.get('fbid')
            fbAuth = self.request.get('fbauth')
            verifiedArtistData = models.GetVerifiedArtist(loadedJson, currentUserId, fbID = fbID, fbAuth = fbAuth)
        else:
            verifiedArtistData = models.GetVerifiedArtist(loadedJson, currentUserId)
        verifiedJson = json.dumps(verifiedArtistData)

        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(verifiedJson)
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/verify(.*)', VerificationHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
