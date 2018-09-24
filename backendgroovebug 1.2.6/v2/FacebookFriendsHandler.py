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
import urllib2, urllib, datetime
from datetime import tzinfo, timedelta, datetime
import DataModels as models
import echonestlib as echonest
import facebook, random, logging
logging.getLogger().setLevel(logging.DEBUG)



class FacebookFriendsHandler(webapp.RequestHandler):
    """ Class that handles requests for a users friends and friend composite page links.
        The handler requires a groovebug user ID and a facebook authentication token
        as 'user' and 'fbauth' parameters respectively."""
    def get(self, fbauth):
## Use groovebug ID to retrieve user library and favorites list.
        logging.info('START')
        currentUserId = self.request.get("user")
        currentUserId = currentUserId.encode('utf-8')
        currentUser = models.GroovebugUser.get_by_key_name(currentUserId)
        userArtistList = currentUser.artistList
        if currentUser.artistList:
            if currentUser.artistList is None:
                userArtistList = []
            else:
                userArtistList = currentUser.artistList
        else:
            userArtistList = []
            
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
        friendInDS = []

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

        friendProfIDs = []
        if not currentFacebookUser.friendsData is None:
            friendsProfileAndLikes = json.loads(currentFacebookUser.friendsData)
            for index, friend in enumerate(friendsProfileAndLikes):
                friendProfIDs.append(friend['id'])
        else:
            friendsProfileAndLikes = []   
            
        if currentFacebookUser.friendsIDList:
            friendsIDList = currentFacebookUser.friendsIDList
        else:
            friendsIDList = []
        

        for index, friend in enumerate(friendsData['data']):
            friendIDs.append(friend['id'])
            
        freshSetofIds = set(friendIDs)
        cachedSetofIds = set(friendsIDList)
        cachedProfIds = set(friendProfIDs)
        profileChk = cachedSetofIds - cachedProfIds
        newSetofFriends = freshSetofIds - cachedSetofIds
        setofFriendsDeleted = cachedSetofIds - freshSetofIds
        logging.info('user has ' + str(len(friendsIDList)) + ' friends already verified')

        if len(profileChk) > 0:
            logging.info('user has ' + str(len(profileChk)) + ' friends, that are not written in their friends data')
            for index, friendID in enumerate(profileChk):
                testFacebookUser = models.FacebookUser.get_by_key_name(friendID)
                if not testFacebookUser is None:
                    facebookFavorites = []
                    profile = {}
                    profile['name'] = testFacebookUser.name
                    profile['id'] = friendID
                    profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + friendID + '&fbauth=' + auth_token
                    profile['profile picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=square"

                    profile['match'] = {}
                    groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
                    for gbugUser in groovebugUsers:
                        if gbugUser.facebookID == profile['id']:
                            facebookFavorites = gbugUser.groovebugFavorites
                    
                    if facebookFavorites == []:
                        if testFacebookUser.fbArtistList:
                            if testFacebookUser.fbArtistList is None:
                                if testFacebookUser.fbArtistListString == "":
                                    #logging.info('friend ' + str(index+1) + ' of ' + str(len(newSetofFriends)) + ' has no likes')
                                    #profile['music likes'] = []
                                    profile['match']['library'] = 0.0
                                    profile['match']['favorites'] = 0.0
                                    friendsProfileAndLikes.append(profile)
                                    #friendsIDList.append(friendID)
                                else:
                                    pass
                                    #logging.info('FB User ' + str(friendID) + ' has a missing artist list, list is none')
                            else:
                                profile['match']['library'] = str(models.GetFriendsTileScore(testFacebookUser.fbArtistList, userArtistList))
                                profile['match']['favorites'] = str(models.GetFriendsTileScore(testFacebookUser.fbArtistList, userFavorites))
                                friendsProfileAndLikes.append(profile)
                                #friendsIDList.append(friendID)
                        else:
                            if testFacebookUser.fbArtistListString == "":
                                profile['match']['library'] = 0.0
                                profile['match']['favorites'] = 0.0
                                friendsProfileAndLikes.append(profile)
                                #friendsIDList.append(friendID)
                            else:
                                pass
                    else:
                        profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                        profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                        friendsProfileAndLikes.append(profile)
                        #friendsIDList.append(friendID)
        
        if len(newSetofFriends) > 0:
            logging.info('user has ' + str(len(newSetofFriends)) + ' new friends, checking datastore for them')
            for index, friendID in enumerate(newSetofFriends):
                testFacebookUser = models.FacebookUser.get_by_key_name(friendID)
                if not testFacebookUser is None:
                    facebookFavorites = []
                    profile = {}
                    profile['name'] = testFacebookUser.name
                    profile['id'] = friendID
                    profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + friendID + '&fbauth=' + auth_token
                    profile['profile picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=square"
                    #profile['small picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=small"
                    #profile['normal picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=normal"
                    #profile['large picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=large"
                    
                    profile['match'] = {}
                    groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
                    for gbugUser in groovebugUsers:
                        if gbugUser.facebookID == profile['id']:
                            facebookFavorites = gbugUser.groovebugFavorites
                    
                    if facebookFavorites == []:
                        if testFacebookUser.fbArtistList:
                            if testFacebookUser.fbArtistList is None:
                                if testFacebookUser.fbArtistListString == "":
                                    #logging.info('friend ' + str(index+1) + ' of ' + str(len(newSetofFriends)) + ' has no likes')
                                    #profile['music likes'] = []
                                    profile['match']['library'] = 0.0
                                    profile['match']['favorites'] = 0.0
                                    friendsProfileAndLikes.append(profile)
                                    friendsIDList.append(friendID)
                                else:
                                    pass
                                    #friendIDs.append(friendID)
                                    #logging.info('FB User ' + str(friendID) + ' has a missing artist list, list is none')
                            else:
                                ## Get match percents for each friend.
                                #logging.info('getting match percent for friend ' + str(index+1) + ' of ' + str(len(newSetofFriends)))
                                #profile['music likes'] = testFacebookUser.fbArtistList
                                profile['match']['library'] = str(models.GetFriendsTileScore(testFacebookUser.fbArtistList, userArtistList))
                                profile['match']['favorites'] = str(models.GetFriendsTileScore(testFacebookUser.fbArtistList, userFavorites))
                                friendsProfileAndLikes.append(profile)
                                friendsIDList.append(friendID)
                        else:
                            if testFacebookUser.fbArtistListString == "":
                                #logging.info('friend ' + str(index+1) + ' of ' + str(len(newSetofFriends)) + ' has no likes')
                                #profile['music likes'] = []
                                profile['match']['library'] = 0.0
                                profile['match']['favorites'] = 0.0
                                friendsProfileAndLikes.append(profile)
                                friendsIDList.append(friendID)
                            else:
                                pass
                                #friendIDs.append(friendID)
                                #logging.info('FB User ' + str(friendID) + ' has a missing artist list, list is missing')
                    else:
                        ## Get match percents for each friend.
                        #logging.info('getting match percent for friend ' + str(index+1) + ' of ' + str(len(newSetofFriends)))
                        #profile['music likes'] = testFacebookUser.fbArtistList
                        profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                        profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                        friendsProfileAndLikes.append(profile)
                        friendsIDList.append(friendID)
            

            currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
            currentFacebookUser.friendsIDList = friendsIDList
            currentFacebookUser.put()

            freshSetofIds = set(friendIDs)
            cachedSetofIds = set(friendsIDList)
            #dsSetofIds = set(friendInDS)
            newSetofFriends = freshSetofIds - cachedSetofIds
            setofFriendsDeleted = cachedSetofIds - freshSetofIds
            
            logging.info('user has ' + str(len(friendsIDList)) + ' friends already verified, after checking datastore')
        
## If there are any friends added or removed from the stored friends data,
## correct them, if no stored friends data, retrieve from facebook.
        if len(newSetofFriends) > 0:
            try:
                logging.info('user has ' + str(len(newSetofFriends)) + ' new friends, fetching data for them')
                newProfileAndLikesData = graph.Batch_Profile_And_Likes_Request(newSetofFriends)
                logging.info(str(len(newProfileAndLikesData)) + ' friends finished batch profile and likes processing')
                newFriendsProfileAndLikes = []
                for index, friendID in enumerate(newProfileAndLikesData):
                    profile = {}
                    profile['match'] = {}
                    profile['name'] = newProfileAndLikesData[friendID]['name']
                    profile['id'] = newProfileAndLikesData[friendID]['id']
                    profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + newProfileAndLikesData[friendID]['id'] + '&fbauth=' + auth_token
                    profile['profile picture'] = newProfileAndLikesData[friendID]['image']
                    #profile['small picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=small"
                    #profile['normal picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=normal"
                    #profile['large picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=large"
                    #profile['music likes'] = newProfileAndLikesData[friendID]['music likes']
                    facebookFavorites = newProfileAndLikesData[friendID]['music likes']
                    groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
                    for gbugUser in groovebugUsers:
                        if gbugUser.facebookID == profile['id']:
                            facebookFavorites = gbugUser.groovebugFavorites
                    ## Get match percents for each friend.
                    #logging.info('getting match percent for friend ' + str(index+1) + ' of ' + str(len(friendsProfileAndLikes)))
                    profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                    profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                    friendsProfileAndLikes.append(profile)
                    friendsIDList.append(newProfileAndLikesData[friendID]['id'])

            except runtime.DeadlineExceededError:
                logging.info('Timed out, but finished processing ' + str(len(friendsProfileAndLikes)) + ' friends')
                raise Exception('covering our asses')


        #if len(setofFriendsDeleted) > 0:
        #    logging.info('user has deleted ' + str(len(newSetofFriends)) + ' friends from facebook, deleting them')
        #    friendsProfileAndLikes[:] = [profile for profile in friendsProfileAndLikes if not profile['id'] in setofFriendsDeleted]
        #    friendsIDList[:] = [friendID for friendID in friendsIDList if not friendID in setofFriendsDeleted]

        
        currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
        currentFacebookUser.friendsIDList = friendsIDList
        currentFacebookUser.groovebug_UDID = currentUserId
        currentFacebookUser.put()

## Sort friends based on library match and output final Json string
        def matchFloat(x): return float(x['match']['library']);
        friendsProfileAndLikes = sorted(friendsProfileAndLikes, key=matchFloat, reverse=True)
        finalPreJson['facebook friends'] = friendsProfileAndLikes
        logging.info('FINISH')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v2/friends(.*)', FacebookFriendsHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
