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
import facebook, random



""" Class that handles magazine requests"""
class FacebookFriendsHandler(webapp.RequestHandler):
    def get(self, fbauth):
        finalPreJson = {}
        currentUserId = self.request.get("user")
        currentUserId = currentUserId.encode('utf-8')
        currentUser = models.GroovebugUser.get_by_key_name(currentUserId)
        userArtistList = currentUser.artistList
        userFavorites = currentUser.groovebugFavorites

        finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'user' : currentUserId}
        finalPreJson['facebook friends'] = []
        
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object("me")          
        friendsData = graph.get_connections(userProfile["id"], "friends")
        friendIDs = []
        for index, friend in enumerate(friendsData['data']):
            friendIDs.append(friend['id'])
        friendsProfileData = graph.Batch_Profile_Request(friendIDs)
        friendsMusicLikesData = graph.Batch_Music_Likes_Request(friendIDs)
        friendsProfileAndLikes = []
        for friendID in friendsProfileData:
            profile = {}
            profile['match'] = {}
            profile['name'] = friendsProfileData[friendID]['name']
            profile['tile page'] = 'http://' + str(hostUrl) + '/v1/fbfriendtile?id=' + friendsProfileData[friendID]['id'] + '&fbauth=' + auth_token
            profile['profile picture'] = friendsProfileData[friendID]['image']
            
            facebookFavorites = friendsMusicLikesData[friendID]
            if not facebookFavorites == []:
                correctedFacebookFavorites = echonest.CorrectArtistNames(facebookFavorites)
                facebookFavorites = []
                for artist in correctedFacebookFavorites:
                    if artist != None:
                        facebookFavorites.append(artist)
                profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
            else:
                profile['match']['library'] = str(random.randint(0, 100))
                profile['match']['favorites'] = str(random.randint(0, 100))
            
            friendsProfileAndLikes.append(profile)
            
        finalPreJson['facebook friends'] = friendsProfileAndLikes
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/fbfriends(.*)', FacebookFriendsHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
