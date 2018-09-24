""" This is the handler for the home bapge of the backend.
    If a user is not logged in to facebook, a login button will appear
    prompting the user to log in to facebook and grand our app
    the appropriate permissions that we need. If a user is logged
    in, a list of artists that they have liked on facebook
    will pulled, saved to our database under the class
    FacebookUser with their facebook user id as the keyname."""

FACEBOOK_APP_ID = "120878094678054"
FACEBOOK_APP_SECRET = "3537e2de75869e44ebe27bde09836c25"

import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from os import path
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.template import render
from django.utils import simplejson as json
import DataModels as models
import echonestlib as echonest
import facebook



""" Class that handles magazine requests"""
class FacebookFriendHandler(webapp.RequestHandler):
    def get(self, fbauth):
        finalPreJson = {}
        facebookId = self.request.get("id")
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object(facebookId)          
        musicLikes = graph.get_connections(facebookId, "music")

        finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'facebook id' : facebookId}
        finalPreJson['profile'] = []
        
        profile = {}
        profile['name'] = userProfile["name"]
        profile['url'] = userProfile["link"]
        profile['profile picture'] = "http://graph.facebook.com/" + facebookId + "/picture?type=square"
        
        fbArtistList = []
        if musicLikes['data'] != []:
            for artist in musicLikes['data']:
                if artist['category'] == "Musician/band":
                    fbArtistList.append(artist['name'])
        correctedFacebookFavorites = echonest.CorrectArtistNames(fbArtistList)
        facebookFavorites = []
        for artist in correctedFacebookFavorites:
            if artist != None:
                facebookFavorites.append(artist)
        profile['music likes'] = facebookFavorites
        finalPreJson['profile'] = profile
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/fbfriendtile(.*)', FacebookFriendHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
