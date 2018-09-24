""" This is the handler that is responsible for recieving a groovebug
    user id and a facebook authentication token, and returning a json document
    containing facebook friend information and match percents matching a friends
    music likes to the groovebug users library and favorites"""

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
from google.appengine.api import urlfetch, memcache
from django.utils import simplejson as json
import DataModels as models
import echonestlib as echonest
import facebook, random, logging
logging.getLogger().setLevel(logging.DEBUG)



""" Class that handles friends requests"""
class FacebookFriendsHandler(webapp.RequestHandler):
    def get(self, fbauth):
## Use groovebug ID to retrieve user library and favorites list.
        logging.info('START')
        currentUserId = self.request.get("user")
        currentUserId = currentUserId.encode('utf-8')
        currentUser = models.GroovebugUser.get_by_key_name(currentUserId)
        userArtistList = currentUser.artistList
        userFavorites = currentUser.groovebugFavorites
        
## Start to build final dictionary that will be output
        finalPreJson = {}
        finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'user' : currentUserId}
        finalPreJson['facebook friends'] = []

## Use facebook authentication token to get users facebook profile information,
## gather friends IDs, and store facebook ID to users GroovebugUser entry
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object("me")
        currentUser.facebookID = userProfile["id"]
        currentUser.put()
        friendsData = graph.get_connections(userProfile["id"], "friends")
        friendIDs = []
        for index, friend in enumerate(friendsData['data']):
            friendIDs.append(friend['id'])

## Use user's facebook id to retrieve FacebookUser entry, create a new one if
## if none are found, and get stored friends profile and music likes in order
## to reduce calls to facebook and echonest
        currentFacebookUser = models.FacebookUser.get_by_key_name(userProfile["id"])
        if currentFacebookUser is None:
            currentFacebookUser = models.FacebookUser(key_name = userProfile["id"],
                                                      groovebug_UDID = currentUserId,
                                                      name = userProfile["name"],
                                                      profile_url = userProfile["link"],
                                                      access_token = auth_token)
        friendsProfileAndLikes = currentFacebookUser.friendsData
## If there are any friends added or removed from the stored friends data,
## correct them, if no stored friends data, retrieve from facebook.
        if friendsProfileAndLikes is not None:
            friendsProfileAndLikes = json.loads(friendsProfileAndLikes)
            if len(friendIDs) != len(friendsProfileAndLikes):
                logging.info(str(len(friendIDs)) + ' friends from facebook and ' + str(len(friendsProfileAndLikes)) + ' friends from cache, working out differences')
                cachedIds = []
                for profile in friendsProfileAndLikes:
                    cachedIds.append(profile['id'])
                freshSetofIds = set(friendIDs)
                cachedSetofIds = set(cachedIds)
                newSetofFriends = freshSetofIds - cachedSetofIds
                setofFriendsDeleted = cachedSetofIds - freshSetofIds

                if len(newSetofFriends) != 0:
                    logging.info('user has ' + str(len(newSetofFriends)) + ' new friends, fetching data for them')
                    newProfileAndLikesData = graph.Batch_Profile_And_Likes_Request(newSetofFriends)
                    newFriendsProfileAndLikes = []
                    for index, friendID in enumerate(newProfileAndLikesData):
                        profile = {}
                        profile['match'] = {}
                        profile['name'] = newProfileAndLikesData[friendID]['name']
                        profile['id'] = newProfileAndLikesData[friendID]['id']
                        profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + newProfileAndLikesData[friendID]['id'] + '&fbauth=' + auth_token
                        profile['profile picture'] = newProfileAndLikesData[friendID]['image']
                        profile['small picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=small"
                        profile['normal picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=normal"
                        profile['large picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=large"
                        profile['music likes'] = newProfileAndLikesData[friendID]['music likes']
                        friendsProfileAndLikes.append(profile)

                if len(setofFriendsDeleted) != 0:
                    logging.info('user has deleted ' + str(len(newSetofFriends)) + ' friends from facebook, deleting them')
                    friendsProfileAndLikes[:] = [profile for profile in friendsProfileAndLikes if not profile['id'] in setofFriendsDeleted]

                currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
                currentFacebookUser.put()
        else:
            profileAndLikesData = graph.Batch_Profile_And_Likes_Request(friendIDs)
            friendsProfileAndLikes = []
            for index, friendID in enumerate(profileAndLikesData):
                profile = {}
                profile['match'] = {}
                profile['name'] = profileAndLikesData[friendID]['name']
                profile['id'] = profileAndLikesData[friendID]['id']
                profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + profileAndLikesData[friendID]['id'] + '&fbauth=' + auth_token
                profile['profile picture'] = profileAndLikesData[friendID]['image']
                profile['small picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=small"
                profile['normal picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=normal"
                profile['large picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=large"
                profile['music likes'] = profileAndLikesData[friendID]['music likes']
                friendsProfileAndLikes.append(profile)
            currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
            currentFacebookUser.put()

## Get match percents for each friend.
        for index, profile in enumerate(friendsProfileAndLikes):
            facebookFavorites = profile['music likes']
            logging.info('getting match percent for friend ' + str(index+1) + ' of ' + str(len(friendsProfileAndLikes)))
            profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
            profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))

## Sort friends based on library match and output final Json string
        def matchFloat(x): return float(x['match']['library']);
        friendsProfileAndLikes = sorted(friendsProfileAndLikes, key=matchFloat, reverse=True)
        finalPreJson['facebook friends'] = friendsProfileAndLikes
        logging.info('FINISH')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v2/friends(.*)', FacebookFriendsHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
