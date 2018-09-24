""" This is the handler that is responsible for recieving a groovebug
    user id and a facebook authentication token, and returning a json document
    containing facebook friend information and match percents matching a friends
    music likes to the groovebug users library and favorites"""

FACEBOOK_APP_ID = "120878094678054"
FACEBOOK_APP_SECRET = "3537e2de75869e44ebe27bde09836c25"
FACEBOOK_UPDATE_DAYS = 7

import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch, taskqueue
from django.utils import simplejson as json
from datetime import datetime
import DataModels as models
import facebook, logging
logging.getLogger().setLevel(logging.DEBUG)



class FacebookFriendsHandler(webapp.RequestHandler):
    """ Class that handles requests for a users friends and friend composite page links.
        The handler requires a groovebug user ID and a facebook authentication token
        as 'user' and 'fbauth' parameters respectively."""
    def get(self, fbauth):
## Use groovebug ID to retrieve user library and favorites list.
        logging.info('START')
        todaysDate = datetime.utcnow()
        timeToUpdate = False
        
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
        finalPreJson['status']['incomplete'] = False
        finalPreJson['facebook friends'] = []

## Use facebook authentication token to get users facebook profile information,
## gather friends IDs, and store facebook ID to users GroovebugUser entry
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object("me")
## Store facebook ID within GroovebugUser Entity
        currentUser.facebookID = userProfile["id"]
        currentUser.put()
        friendsData = graph.get_connections(userProfile["id"], "friends")
        friendIDs = []
        #friendInDS = []
        favsCheckList = []
## Use user's facebook id to retrieve FacebookUser entry, create a new one if
## if none are found, and get stored friends profile and music likes in order
## to reduce calls to facebook and echonest
        currentFacebookId = userProfile["id"]
        currentFacebookUser = models.FacebookUser.get_by_key_name(userProfile["id"])
        if currentFacebookUser is None:
            currentFacebookUser = models.FacebookUser(key_name = userProfile["id"],
                                                      name = userProfile["name"],
                                                      profile_url = userProfile["link"],
                                                      access_token = auth_token)
## If there is already a FacebookUser entity, add access token to entity in order
## to show that facebook user has logged in using groovebug
        else:
            currentFacebookUser.access_token = auth_token
        currentFacebookUser.put()

## Check to see how long ago the current facebook user has logged into groovebug
## and set timeToUpdate variable to True if time is more than FACEBOOK_UPDATE_DAYS
## in order to show that friends data needs to be updated
        tdelta = todaysDate - currentFacebookUser.updated
        logging.info('users facebook info was updated ' + str(tdelta.days) + ' days ago')
        if tdelta.days >= FACEBOOK_UPDATE_DAYS:
            timeToUpdate = True
          
## Load facebook profile and music likes for facebook friends from datastore if they are there and
## gather facebook ids from the data  
        friendProfIDs = []
        if not currentFacebookUser.friendsData is None and not timeToUpdate:
            friendsProfileAndLikes = json.loads(currentFacebookUser.friendsData)
        else:
            friendsProfileAndLikes = []   

## Load saved list of friends IDs from FacebookUser entity if it is found            
        if currentFacebookUser.friendsIDList:
            friendsIDList = currentFacebookUser.friendsIDList
        else:
            friendsIDList = []
        
## Gather a fresh set of facebook friends' ids from facebook url response.
        for friend in friendsData['data']:
            friendIDs.append(friend['id'])

        profileChk = []
            
        freshSetofIds = set(friendIDs)
        cachedSetofIds = set(friendsIDList)

## If id list from datastore is longer than the length of the saved facebook friends data,
## make a list of new ids to check and fetch. This case should never happen, but was happening
## after the update was made because the FacebookCrawler was still running. It has since
## been stopped.
        if len(friendsIDList) > len(friendsProfileAndLikes):
            for friend in friendsProfileAndLikes:
                friendProfIDs.append(friend['id'])
            cachedProfIds = set(friendProfIDs)
            profileChk = cachedSetofIds - cachedProfIds
        #else:
        #    profileChk = []
            
        newSetofFriends = freshSetofIds - cachedSetofIds
        setofFriendsDeleted = cachedSetofIds - freshSetofIds
        logging.info('user has ' + str(len(friendsIDList)) + ' friends already verified')

## If there are profiles missing from the cached profile and likes information,
## check the datastore for a corresponding FacebookUser entity and update the cached
## profile and likes data if found.
        if len(profileChk) > 0:
            logging.info('user has ' + str(len(profileChk)) + ' friends that need to be re-checked')
                
            for friendID in profileChk:
                testFacebookUser = models.FacebookUser.get_by_key_name(friendID)
                fTimeToUpdate = False
                if not testFacebookUser is None:
                    facebookFavorites = []
                    profile = {}
                    profile['name'] = testFacebookUser.name
                    profile['id'] = friendID
                    profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + friendID + '&fbauth=' + auth_token
                    profile['profile picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=square"

                    profile['groovebug user'] = False
                    facebookUserEntity = models.FacebookUser.get_by_key_name(profile["id"])
                    if facebookUserEntity is not None:
                        gbugUser = facebookUserEntity.groovebug_user_set.get()
                        if gbugUser is not None:
                            facebookFavorites = gbugUser.groovebugFavorites
                            profile['groovebug user'] = True
##                    groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
##                    for gbugUser in groovebugUsers:
##                        if gbugUser.facebookID == profile['id']:
##                            facebookFavorites = gbugUser.groovebugFavorites
##                            profile['groovebug user'] = True
                        
                    if facebookFavorites == []:
                        tdelta = todaysDate - currentFacebookUser.updated
                        if tdelta.days >= FACEBOOK_UPDATE_DAYS:
                            fTimeToUpdate = True
                            
                        if testFacebookUser.fbArtistListVerified and not(fTimeToUpdate or timeToUpdate):
                            profile['match'] = {}
                            if testFacebookUser.fbArtistList:
                                if not testFacebookUser.fbArtistList is None:
                                    facebookFavorites = testFacebookUser.fbArtistList

                            if len(facebookFavorites) > 0:
                                profile['match']['artist count'] = len(facebookFavorites)
                                if len(userArtistList):
                                    profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                                else:
                                    profile['match']['library'] = str(0.0)
                                if len(userFavorites) > 0:
                                    profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                                else:
                                    profile['match']['favorites'] = str(0.0)
                            else:
                                profile['match']['artist count'] = 0
                                profile['match']['library'] = str(0.0)
                                profile['match']['favorites'] = str(0.0)
                        else:
                            favsCheckList.append(friendID)
                            
                    else:
                        profile['match'] = {}
                        profile['match']['artist count'] = len(facebookFavorites)
                        profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                        profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))

                    friendsProfileAndLikes.append(profile)
                    #friendsIDList.append(friendID)

            currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
            #currentFacebookUser.friendsIDList = friendsIDList
            currentFacebookUser.put()

##         
        if len(newSetofFriends) > 0:
            logging.info('user has ' + str(len(newSetofFriends)) + ' new friends, checking datastore for them')
            for friendID in newSetofFriends:
                testFacebookUser = models.FacebookUser.get_by_key_name(friendID)
                if not testFacebookUser is None:
                    facebookFavorites = []
                    profile = {}
                    profile['name'] = testFacebookUser.name
                    profile['id'] = friendID
                    profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + friendID + '&fbauth=' + auth_token
                    profile['profile picture'] = "http://graph.facebook.com/" + profile['id'] + "/picture?type=square"          
                    profile['groovebug user'] = False
                    facebookUserEntity = models.FacebookUser.get_by_key_name(profile["id"])
                    if facebookUserEntity is not None:
                        gbugUser = facebookUserEntity.groovebug_user_set.get()
                        if gbugUser is not None:
                            facebookFavorites = gbugUser.groovebugFavorites
                            profile['groovebug user'] = True
##                    groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
##                    for gbugUser in groovebugUsers:
##                        if gbugUser.facebookID == profile['id']:
##                            facebookFavorites = gbugUser.groovebugFavorites
##                            profile['groovebug user'] = True
                    
                    if facebookFavorites == []:
                        if testFacebookUser.fbArtistListVerified:
                            profile['match'] = {}
                            if testFacebookUser.fbArtistList:
                                if not testFacebookUser.fbArtistList is None:
                                    facebookFavorites = testFacebookUser.fbArtistList

                            if len(facebookFavorites) > 0:
                                profile['match']['artist count'] = len(facebookFavorites)
                                if len(userArtistList) > 0:
                                    profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                                else:
                                    profile['match']['library'] = str(0.0)
                                if len(userFavorites) > 0:
                                    profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                                else:
                                    profile['match']['favorites'] = str(0.0)
                            else:
                                profile['match']['artist count'] = 0
                                profile['match']['library'] = str(0.0)
                                profile['match']['favorites'] = str(0.0)
                        else:
                            favsCheckList.append(friendID)
                            
                    else:
                        profile['match'] = {}
                        profile['match']['artist count'] = len(facebookFavorites)
                        profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                        profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))

                    friendsProfileAndLikes.append(profile)
                    friendsIDList.append(friendID)
            

            currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
            currentFacebookUser.friendsIDList = friendsIDList
            currentFacebookUser.put()

            freshSetofIds = set(friendIDs)
            cachedSetofIds = set(friendsIDList)
            newSetofFriends = freshSetofIds - cachedSetofIds
            setofFriendsDeleted = cachedSetofIds - freshSetofIds
            
            logging.info('user has ' + str(len(friendsIDList)) + ' friends already verified, after checking datastore')
        
## If there are any friends added or removed from the stored friends data,
## correct them, if no stored friends data, retrieve from facebook.
        if len(newSetofFriends) > 0:
            try:
                logging.info('user has ' + str(len(newSetofFriends)) + ' new friends, fetching data for them')
                newProfileAndLikesData = graph.Batch_Profile_Request(newSetofFriends)
                logging.info(str(len(newProfileAndLikesData)) + ' friends finished batch profile and likes processing')
                #newFriendsProfileAndLikes = []
                
                for friendID in newProfileAndLikesData:
                    musicVerified = False
                    profile = {}
                    profile['name'] = newProfileAndLikesData[friendID]['name']
                    profile['id'] = newProfileAndLikesData[friendID]['id']
                    profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + newProfileAndLikesData[friendID]['id'] + '&fbauth=' + auth_token
                    profile['profile picture'] = newProfileAndLikesData[friendID]['image']
                    #profile['music likes'] = newProfileAndLikesData[friendID]['music likes']
                    if newProfileAndLikesData[friendID]['likes verified']:
                        facebookFavorites = newProfileAndLikesData[friendID]['music likes']
                        musicVerified = True
                    else:
                        favsCheckList.append(friendID)
                        facebookFavorites = []

                    profile['groovebug user'] = False
                    facebookUserEntity = models.FacebookUser.get_by_key_name(profile["id"])
                    if facebookUserEntity is not None:
                        gbugUser = facebookUserEntity.groovebug_user_set.get()
                        if gbugUser is not None:
                            facebookFavorites = gbugUser.groovebugFavorites
                            profile['groovebug user'] = True
                            musicVerified = True
##                    groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
##                    for gbugUser in groovebugUsers:
##                        if gbugUser.facebookID == profile['id']:
##                            facebookFavorites = gbugUser.groovebugFavorites
##                            profile['groovebug user'] = True
##                            musicVerified = True
                            
                    ## Get match percents for each friend.
                    #logging.info('getting match percent for friend ' + str(index+1) + ' of ' + str(len(friendsProfileAndLikes)))
                    if facebookFavorites != []:
                        profile['match'] = {}
                        profile['match']['artist count'] = len(facebookFavorites)
                        if len(userArtistList) > 0:
                            profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                        else:
                            profile['match']['library'] = str(0.0)
                        if len(userFavorites) > 0:
                            profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                        else:
                            profile['match']['favorites'] = str(0.0)        
                    else:
                        if musicVerified:
                            profile['match'] = {}
                            profile['match']['artist count'] = 0
                            profile['match']['library'] = str(0.0)
                            profile['match']['favorites'] = str(0.0)
                            
                    friendsProfileAndLikes.append(profile)
                    friendsIDList.append(newProfileAndLikesData[friendID]['id'])

                    
            except urlfetch.DeadlineExceededError:
                logging.info('Timed out, but finished processing ' + str(len(friendsProfileAndLikes)) + ' friends')

        if len(setofFriendsDeleted) > 0:
            logging.info('user has deleted ' + str(len(setofFriendsDeleted)) + ' friends from facebook, deleting them')
            friendsProfileAndLikes[:] = [profile for profile in friendsProfileAndLikes if not profile['id'] in setofFriendsDeleted]
            friendsIDList[:] = [friendID for friendID in friendsIDList if not friendID in setofFriendsDeleted]

        currChklist = []
        if currentFacebookUser.friendsToChkList:
            if not currentFacebookUser.friendsToChkList is None:
                currChklist = currentFacebookUser.friendsToChkList

        if len(currChklist) > 0:
            finalPreJson['status']['incomplete'] = True
            favsCheckList = []
            logging.info('The last background job for this user has not finished')
        else:
            for friend in friendsProfileAndLikes:
                if not friend.has_key('match'):
                    finalPreJson['status']['incomplete'] = True
                    if friend['id'] not in favsCheckList:
                        favsCheckList.append(friend['id'])
                    #logging.info('Friend ' + str(friend['name']) + ', ID ' + str(friend['id']) + ', does not have a verified favorites list')
            currentFacebookUser.friendsToChkList = favsCheckList
        
        currentFacebookUser.groovebug_UDID = currentUserId
        currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
        currentFacebookUser.friendsIDList = friendsIDList
        currentFacebookUser.put()
            
        if len(favsCheckList) > 0:
            taskqueue.add(url='/v2/friendsworker', params={'groovebugId': currentUserId, 'facebookId': currentFacebookId, 'fbauth': auth_token})
            logging.info('Added task queue for ' + str(len(favsCheckList)) + ' friends')
            logging.info('The list to check is ' + str(favsCheckList))

            
## Sort friends based on library match and output final Json string
        #def matchFloat(x): return float(x['match']['library']);
        #friendsProfileAndLikes = sorted(friendsProfileAndLikes, key=matchFloat, reverse=True)
        finalPreJson['facebook friends'] = friendsProfileAndLikes
        logging.info('FINISH')

        currentUser.facebookProfile = currentFacebookUser
        currentUser.put()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))


class FacebookFriendsWorker(webapp.RequestHandler):        
    def post(self): # should run at most 1/s
        logging.info('It got to the POST') 
        groovebugID = self.request.get('groovebugId')
        facebookID = self.request.get('facebookId')
        auth_token = self.request.get('fbauth')
        #friendsChkList = json.loads(self.request.get('friendsList'))
        self.chkFavs(groovebugID, facebookID, auth_token)
        #self.chkFavs(groovebugID, facebookID, auth_token, friendsChkList)

    def chkFavs(self, groovebugID, facebookID, auth_token):
        logging.info('It got to the chkFavs')
        #auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object("me")
        friendsData = graph.get_connections(userProfile["id"], "friends")
        #friendsList = []
        currentUser = models.GroovebugUser.get_by_key_name(groovebugID)
        #userArtistList = currentUser.artistList
        if currentUser.artistList:
            if currentUser.artistList is None:
                userArtistList = []
            else:
                userArtistList = currentUser.artistList
        else:
            userArtistList = []
    
        #userFavorites = currentUser.groovebugFavorites
        if currentUser.groovebugFavorites:
            if currentUser.groovebugFavorites is None:
                userFavorites = []
            else:
                userFavorites = currentUser.groovebugFavorites
        else:
            userFavorites = []
        logging.info('Starting background task for Groovebug user ' + str(groovebugID) + ', Facebook user ' + str(facebookID))
        
        currentFacebookUser = models.FacebookUser.get_by_key_name(facebookID)
        if not currentFacebookUser is None:
            if currentFacebookUser.friendsToChkList:
                if currentFacebookUser.friendsToChkList is None:
                    friendsChkList = []
                else:
                    if len(currentFacebookUser.friendsToChkList) > 0:
                        friendsChkList = currentFacebookUser.friendsToChkList
                    else:
                        friendsChkList = []
            else:
                friendsChkList = []
                
            logging.info('The list to check is ' + str(friendsChkList))    
            if len(friendsChkList) > 0:
                newChkList = friendsChkList
                if not currentFacebookUser.friendsData is None:
                    friendsProfileAndLikes = json.loads(currentFacebookUser.friendsData)
                else:
                    friendsProfileAndLikes = []

                if not currentFacebookUser.friendsIDList is None:
                    friendsIDList = currentFacebookUser.friendsIDList
                else:
                    friendsIDList = []
                
                try:
                    logging.info('user has ' + str(len(friendsChkList)) + ' friends to process favorites for, fetching data for them')
                    logging.info('the list - ' + str(friendsChkList))
                    for chkID in friendsChkList:
                        chkList = []
                        chkList.append(chkID)
                        newProfileAndLikesData = graph.Batch_Profile_And_Likes_Request(chkList)
                        #logging.info(str(len(newProfileAndLikesData)) + ' friends finished batch profile and likes processing')
                        
                        for friendID in newProfileAndLikesData:
                            profile = {}
                            profile['name'] = newProfileAndLikesData[friendID]['name']
                            profile['id'] = newProfileAndLikesData[friendID]['id']
                            profile['friend url'] = 'http://' + str(hostUrl) + '/v2/friend?id=' + newProfileAndLikesData[friendID]['id'] + '&fbauth=' + auth_token
                            profile['profile picture'] = newProfileAndLikesData[friendID]['image']

                            if newProfileAndLikesData[friendID]['music likes']:
                                facebookFavorites = newProfileAndLikesData[friendID]['music likes']
                            else:
                                facebookFavorites = []
                            
                            facebookUserEntity = models.FacebookUser.get_by_key_name(profile["id"])
                            if facebookUserEntity is not None:
                                gbugUser = facebookUserEntity.groovebug_user_set.get()
                                if gbugUser is not None:
                                    facebookFavorites = gbugUser.groovebugFavorite
                                    profile['groovebug user'] = True           
##                            groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = profile["id"])
##                            for gbugUser in groovebugUsers:
##                                if gbugUser.facebookID == profile['id']:
##                                    facebookFavorites = gbugUser.groovebugFavorites
##                                    musicVerified = True
                                    
                            ## Get match percents for each friend.
                            #logging.info('getting match percent for friend ' + str(index+1) + ' of ' + str(len(friendsProfileAndLikes)))
                            if facebookFavorites != []:
                                profile['match'] = {}
                                profile['match']['artist count'] = len(facebookFavorites)
                                if len(userArtistList) > 0:
                                    profile['match']['library'] = str(models.GetFriendsTileScore(facebookFavorites, userArtistList))
                                else:
                                    profile['match']['library'] = str(0.0)
                                if len(userFavorites) > 0:
                                    profile['match']['favorites'] = str(models.GetFriendsTileScore(facebookFavorites, userFavorites))
                                else:
                                    profile['match']['favorites'] = str(0.0)        
                            else:
                                profile['match'] = {}
                                profile['match']['artist count'] = 0
                                profile['match']['library'] = str(0.0)
                                profile['match']['favorites'] = str(0.0)

                            profileFound = False
                            for entry in friendsProfileAndLikes:
                                #logging.info('checking user ID ' + str(entry['id']) + ' to FB ID ' + str(facebookId))
                                if entry['id'] == profile['id']:
                                    entry['match'] = profile['match']
                                    profileFound = True
                                    break

                            if not profileFound:        
                                friendsProfileAndLikes.append(profile)

                            if not profile['id'] in friendsIDList:
                                friendsIDList.append(profile['id'])
                                
                        newChkList = [x for x in newChkList if x != chkID]

                        currentFacebookUser.friendsToChkList = newChkList
                        currentFacebookUser.friendsData = json.dumps(friendsProfileAndLikes)
                        currentFacebookUser.friendsIDList = friendsIDList
                        currentFacebookUser.put()

                    logging.info('Finished processing background job')
                    
                except urlfetch.DeadlineExceededError:
                    logging.info('Timed out, but finished processing ' + str(len(friendsProfileAndLikes)) + ' friends')    

        #db.run_in_transaction(chkFavs)


""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v2/friendsworker', FacebookFriendsWorker),
                                      ('/v2/friends(.*)', FacebookFriendsHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
