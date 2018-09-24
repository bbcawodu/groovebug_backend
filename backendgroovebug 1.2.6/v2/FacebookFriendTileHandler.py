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
import facebook, urllib2, urllib, re



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
            if post.has_key('application'):
                if post['application'] != None:
                    if post['application'].has_key('name'):
                        if post['application']['name'] == 'Groovebug':
                            groovebugRecentActivity = True
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
        for artist in correctedFacebookFavorites:
            if artist != None:
                artistDictEntry = {}
                artistDictEntry['name'] = artist
                artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
                facebookFavorites.append(artistDictEntry)
        profile['music likes'] = facebookFavorites

## Check Groovebug user entities to see if facebook user has a grooebug account
## and add favorites if found
        profile['groovebugid'] = ""
        groovebugUsers = models.GroovebugUser.gql("WHERE facebookID = :facebookID", facebookID = userProfile["id"])
        if groovebugUsers is not None:
            for user in groovebugUsers:
                if user.userId is not None:
                    profile['groovebugid'] = user.userId
                if user.groovebugFavorites is not None:
                    groovebugFavorites = user.groovebugFavorites
                    groovebugFavoritesData = []
                    for artist in groovebugFavorites:
                        artistDictEntry = {}
                        artistDictEntry['name'] = artist
                        artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
                        groovebugFavoritesData.append(artistDictEntry)
                    profile['favorites'] = groovebugFavoritesData
        finalPreJson['profile'] = profile
        
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
        for post in userWall['data']:
            if post.has_key('application'):
                if post['application'] != None:
                    if post['application'].has_key('name'):
                        if post['application']['name'] == 'Groovebug':
                            if groovebugIcon == None:
                                groovebugIcon = post['icon']
                            groovebugPost = {}
                            groovebugPost['text'] = post['message']
                            
                            date = re.sub(r'T', '<br/>', post['created_time'])
                            date = re.sub(r'^', 'Date: ', date)
                            date = re.sub(r'<br/>', '<br/> Time: ', date)
                            groovebugPost['date'] = re.sub(r'(\+)(.*)', '', date)
                            
                            groovebugPost['from'] = {}
                            groovebugPost['from']['name'] = post['from']['name']
                            groovebugPost['from']['id'] = post['from']['id']
                            if post.has_key('link'):
                                groovebugPost['link'] = post['link']
                                groovebugPost['linkPreview'] = post['picture']
                                groovebugPost['linkName'] = post['name']
                            recentActivity.append(groovebugPost)

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
