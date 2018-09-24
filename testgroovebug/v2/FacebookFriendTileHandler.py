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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.template import render
from django.utils import simplejson as json
import DataModels as models
import echonestlib as echonest
import facebook, urllib, re, logging
logging.getLogger().setLevel(logging.DEBUG)



class FacebookFriendHandler(webapp.RequestHandler):
    """ Class that handles individual facebook friend requests"""
    def get(self, fbauth):
## Get facebook profile and music likes from Facebook Open Graph
## Note: We can only access the news feed of a user that we have an authentication token for
        profilePicturesID = None
        profilePictures = None
        facebookId = self.request.get("id")
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userProfile = graph.get_object(facebookId)          
        musicLikes = graph.get_connections(facebookId, "music")
        photoAlbums = graph.get_connections(facebookId, "albums")

        groovebugRecentActivity = False
        userWall = graph.get_connections(facebookId, "feed")
        for post in userWall['data']:
            groovebugRecentActivity = CheckPostForGroovebug(post)
            if groovebugRecentActivity == True:
                break
##        userNewsFeed = graph.get_connections(facebookId, "home")
##        userLinks = graph.get_connections(facebookId, "links")
##        userPosts = graph.get_connections(facebookId, "posts")
##        userStatuses = graph.get_connections(facebookId, "statuses")
##        userVideosandVideosTaggedIn = graph.get_connections(facebookId, "videos")
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
        finalPreJson['status'] = {'error' : '0', 'version' : '2.0', 'facebook id' : facebookId}
        finalPreJson['background'] = 'http://' + str(hostUrl) + '/v2/fbfriendbackgrounds?id=' + facebookId + '&fbauth=' + auth_token
        finalPreJson['profile'] = []

## Start to build facebook profile dictionary       
        profile = {}
        profile['name'] = userProfile["name"]
        profile['url'] = userProfile["link"]
        if groovebugRecentActivity == True:
            profile['recent activity'] = 'http://' + str(hostUrl) + "/v2/fbrecentactivity?id=" + facebookId + '&fbauth=' + auth_token
        else:
            profile['recent activity'] = ''
        profile['profile picture'] = "http://graph.facebook.com/" + facebookId + "/picture?type=square"
        profile['small picture'] = "http://graph.facebook.com/" + facebookId + "/picture?type=small"
        profile['normal picture'] = "http://graph.facebook.com/" + facebookId + "/picture?type=normal"
        profile['large picture'] = "http://graph.facebook.com/" + facebookId + "/picture?type=large"
        profile['all profile picture sizes'] = []
        if profilePictures is not None:
            profile['all profile picture sizes'] = profilePictures
        profile['favorites'] = []


## testing wall posting id, name, offset, and length
##        taggedPerson = {}
##        taggedPerson['id'] = facebookId
##        taggedPerson['name'] = profile['name']
##        taggedPerson['offset'] = 0
##        taggedPerson['length'] = len(profile['name'])
##        postArguments = {}
##        postArguments['message_tags'] = {}
##        postArguments['message_tags']['0'] = [taggedPerson]
##        message = profile['name'] + ", I pulled ur facebook likes through groovebug! check us out at groovebug.com. This is brad btw, not spam... what up tho!!!!!"
##        graph.put_wall_post(message, profile_id=facebookId)

## Verify music likes with echonest and add magazine links to them
        fbArtistList = []
        if musicLikes['data'] != []:
            for artist in musicLikes['data']:
                if artist['category'] == "Musician/band":
                    fbArtistList.append(artist['name'])
        correctedFacebookFavorites = echonest.CorrectArtistNames(fbArtistList)
        facebookFavorites = []
        facebookFavoritesList = []
        for artist in correctedFacebookFavorites:
            if artist != None:
                artistDictEntry = {}
                artistDictEntry['name'] = artist
                artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
                facebookFavorites.append(artistDictEntry)
                facebookFavoritesList.append(artist)
        profile['music likes'] = facebookFavorites
        profile['likes verified'] = True

## Check Facebook user entities to see if facebook user is there
## and add/update favorites if found
        friendFacebookUser = models.FacebookUser.get_by_key_name(userProfile["id"])
        if friendFacebookUser is None:
            friendFacebookUser = models.FacebookUser(key_name = userProfile["id"],
                                                     name = userProfile["name"],
                                                     profile_url = userProfile["link"])

        friendFacebookUser.fbArtistListVerified = True
        if len(facebookFavoritesList) > 0:
            logging.info(str(userProfile["name"]) + ' - ' + str(len(facebookFavoritesList)) + ' Facebook Favorites - ' + str(facebookFavoritesList))
            friendFacebookUser.fbArtistList = facebookFavoritesList
        else:
            friendFacebookUser.fbArtistList = []
            friendFacebookUser.fbArtistListString = ""

        friendFacebookUser.put()
                    
## Check Groovebug user entities to see if facebook user has a groovebug account
## and add favorites if found
        profile['groovebugid'] = ""
        groovebugFavoritesList = []
        facebookUserEntity = models.FacebookUser.get_by_key_name(facebookId)
        if facebookUserEntity is not None:
            groovebugUser = facebookUserEntity.groovebug_user_set.get()
            if groovebugUser is not None:
                if groovebugUser.userId is not None:
                    profile['groovebugid'] = groovebugUser.userId
                if groovebugUser.groovebugFavorites is not None:
                    groovebugFavorites = groovebugUser.groovebugFavorites
                    groovebugFavoritesData = []
                    for artist in groovebugFavorites:
                        artistDictEntry = {}
                        artistDictEntry['name'] = artist
                        artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
                        groovebugFavoritesData.append(artistDictEntry)
                        groovebugFavoritesList.append(artist)
                    profile['favorites'] = groovebugFavoritesData
        finalPreJson['profile'] = profile

## Update the match percents of the calling user for
## this friend
        callingFacebookUsers = models.FacebookUser.gql("WHERE access_token  = :accessToken", accessToken = auth_token)
        if callingFacebookUsers is not None:
            for user in callingFacebookUsers:
                callingGroovebugUser = user.groovebug_user_set.get()
                if callingGroovebugUser is not None:
                    userArtistList = callingGroovebugUser.artistList
                    userFavorites = callingGroovebugUser.groovebugFavorites
                    if len(groovebugFavoritesList) > 0:
                        musicFavoritesList = groovebugFavoritesList
                    else:
                        musicFavoritesList = facebookFavoritesList
                        
                    if not user.friendsData is None:
                        friendsProfileAndLikes = json.loads(user.friendsData)
                    else:
                        friendsProfileAndLikes = []   
                    for entry in friendsProfileAndLikes:
                        #logging.info('checking user ID ' + str(entry['id']) + ' to FB ID ' + str(facebookId))
                        if entry['id'] == facebookId:
                            entry['match'] = {}
                            if profile['groovebugid'] != "":
                                entry['groovebug user'] = True
                            if len(musicFavoritesList) > 0:
                                entry['match']['artist count'] = len(musicFavoritesList)
                                if len(userArtistList) > 0:
                                    entry['match']['library'] = str(models.GetFriendsTileScore(musicFavoritesList, userArtistList))
                                else:
                                    entry['match']['library'] = str(0.0)
                                if len(userFavorites) > 0:
                                    entry['match']['favorites'] = str(models.GetFriendsTileScore(musicFavoritesList, userFavorites))
                                else:
                                    entry['match']['favorites'] = str(0.0)
                            else:
                                entry['match']['artist count'] = 0
                                entry['match']['library'] = str(0.0)
                                entry['match']['favorites'] = str(0.0)
                                
                            logging.info('updating match percents for user ' + str(callingGroovebugUser.userId) + ' with friend ' + str(userProfile["name"]))
                    user.friendsData = json.dumps(friendsProfileAndLikes)
                    user.put()
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))



class RecentActivityHandler(webapp.RequestHandler):
    """ Class that handles individual facebook friend requests"""
    def get(self, fbauth):
## Get facebook profile and music likes from Facebook Open Graph
        facebookId = self.request.get("id")
        auth_token = self.request.get('fbauth')
        graph = facebook.GraphAPI(auth_token)
        userWall = graph.get_connections(facebookId, "feed")
        groovebugIcon = None
                
## Start to build final dictionary that will be output
        recentActivity = []
        groovebugIndicator = False
        for post in userWall['data']:
            groovebugIndicator = CheckPostForGroovebug(post)
            if groovebugIndicator == True:
                groovebugPost = {}
                if post.has_key('message'):
                    groovebugPost['text'] = post['message']
                if post.has_key('caption'):
                    groovebugPost['caption'] = post['caption']
                if post.has_key('description'):
                    groovebugPost['description'] = post['description']
                            
                date = re.sub(r'T', '<br/>', post['created_time'])
                date = re.sub(r'^', 'Date: ', date)
                date = re.sub(r'<br/>', '<br/> Time: ', date)
                groovebugPost['date'] = re.sub(r'(\+)(.*)', '', date)
                
                if post.has_key('name'):
                    groovebugPost['postName'] = post['name']            
                groovebugPost['from'] = {}
                groovebugPost['from']['name'] = post['from']['name']
                groovebugPost['from']['id'] = post['from']['id']
                if post.has_key('link'):
                    groovebugPost['link'] = post['link']
                    groovebugPost['linkPreview'] = post['picture']
                    groovebugPost['linkName'] = post['name']
                recentActivity.append(groovebugPost)
            groovebugIndicator = False

        context = {'recentActivity' : recentActivity,
                   'groovebugIcon' : groovebugIcon,}
        tmpl = path.join(path.dirname(__file__), 'RecentActivity.html')
        html = render(tmpl, context)
        self.response.out.write(html)
##
##        finalPreJson = {}
##        finalPreJson['status'] = {'error' : '0', 'version' : '2.0', 'facebook id' : facebookId}
##        finalPreJson['profile information'] = {}
##        finalPreJson['profile information']['user wall'] = userWall['data']
##        self.response.headers['Content-Type'] = 'application/json'
##        self.response.out.write(json.dumps(finalPreJson))



def CheckPostForGroovebug(post):
    """ This function scans a given facebook wall post and returns True if the post is groovebug related,
        and false if it is not"""
    groovebugIndicator = False
    if post.has_key('application'):
        if post['application'] != None:
            if post['application'].has_key('name'):
                if post['application']['name'] == 'Groovebug':
                    groovebugIndicator = True
    if post.has_key('message') and groovebugIndicator == False:
        if re.search(r'(groovebug)|(Groovebug)', post['message']) != None:
            groovebugIndicator = True
    if post.has_key('description') and groovebugIndicator == False:
        if re.search(r'(groovebug)|(Groovebug)', post['description']) != None:
            groovebugIndicator = True
    if post.has_key('link') and groovebugIndicator == False:
        if re.search(r'(groovebug)|(Groovebug)', post['link']) != None:
            groovebugIndicator = True
    if post.has_key('caption') and groovebugIndicator == False:
        if re.search(r'(groovebug)|(Groovebug)', post['caption']) != None:
            groovebugIndicator = True
    if post.has_key('name') and groovebugIndicator == False:
        if re.search(r'(groovebug)|(Groovebug)', post['name']) != None:
            groovebugIndicator = True
    return groovebugIndicator



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v2/friend(.*)', FacebookFriendHandler),
                                      ('/v2/fbrecentactivity(.*)', RecentActivityHandler),
                                      ('/v1/fbfriendtile(.*)', FacebookFriendHandler),],
                                       debug=True)



def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
