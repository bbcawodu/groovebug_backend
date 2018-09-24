""" This is the handler for individual facebook friend composites
    recieves a facebook ID and a facebook authentication token as an input
    and returns a json document with that friends profile information,
    music likes, and groovebug favorites if the user has groovebug"""

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
import facebook, urllib2, urllib



""" Class that handles individual facebook friend requests"""
class FacebookFriendHandler(webapp.RequestHandler):
    def get(self, fbauth):
## Get facebook profile and music likes from Facebook Open Graph
        profilePicturesID = None
        profilePictures = None
        facebookId = self.request.get("id")
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object(facebookId)          
        musicLikes = graph.get_connections(facebookId, "music")
        photoAlbums = graph.get_connections(facebookId, "albums")
        for album in photoAlbums['data']:
            if album['name'] == 'Profile Pictures':
                profilePicturesID = album['id']
        if profilePicturesID is not None:
            profilePicturesData = graph.get_connections(profilePicturesID, "photos")
            profilePictures = []
            for picture in profilePicturesData['data'][0]['images']:
                pictureEntry = {}
                pictureEntry['size'] = str(picture['width']) + 'x' + str(picture['height'])
                pictureEntry['url'] = picture['source']
                profilePictures.append(pictureEntry)
                
            

## Start to build final dictionary that will be output
        finalPreJson = {}
        finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'facebook id' : facebookId}
        finalPreJson['profile'] = []

## Start to build facebook profile dictionary       
        profile = {}
        profile['name'] = userProfile["name"]
        profile['url'] = userProfile["link"]
        profile['profile picture'] = "http://graph.facebook.com/" + facebookId + "/picture?type=square"
        profile['all profile picture sizes'] = []
        if profilePictures is not None:
            profile['all profile picture sizes'] = profilePictures
        profile['favorites'] = []

## Verify music likes with echonest and add magazine links to them
        fbArtistList = []
        if musicLikes['data'] != []:
            for artist in musicLikes['data']:
                if artist['category'] == "Musician/band":
                    fbArtistList.append(artist['name'])
        correctedFacebookFavorites = echonest.CorrectArtistNames(fbArtistList)
        facebookFavorites = []
        for artist in correctedFacebookFavorites:
            if artist != None:
                artistDictEntry = {}
                artistDictEntry['name'] = artist
                artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
                facebookFavorites.append(artistDictEntry)
        profile['music likes'] = facebookFavorites

## Check Groovebug user entities to see if facebook user has a grooebug account
## and add favorites if found
        groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = userProfile["id"])
        if groovebugUsers is not None:
            for user in groovebugUsers:
                if user.groovebugFavoritesJson is not None:
                    profile['favorites'] = json.loads(user.groovebugFavoritesJson)
        finalPreJson['profile'] = profile
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v2/friend(.*)', FacebookFriendHandler),
                                      ('/v1/fbfriendtile(.*)', FacebookFriendHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
