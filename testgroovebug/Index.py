""" This is the handler for the home bapge of the backend.
    If a user is not logged in to facebook, a login button will appear
    prompting the user to log in to facebook and grand our app
    the appropriate permissions that we need. If a user is logged
    in, a list of artists that they have liked on facebook
    will pulled, saved to our database under the class
    FacebookUser with their facebook user id as the keyname."""

FACEBOOK_APP_ID = "165771780180103"
FACEBOOK_APP_SECRET = "f13b46bb31096fb5e1eebe3ff3c328a2"

import facebook
import os
from os import path
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.template import render
import json
import DataModels as models



""" This is a base handler that is responsible for checking if the user
    is logged in, and pulling the user's fb information and storing it
    when they do log in."""
class BaseHandler(webapp.RequestHandler):
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_user_from_cookie(
                self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                graph = facebook.GraphAPI(cookie["access_token"])
                userProfile = graph.get_object("me")
                musicLikes = graph.get_connections(userProfile["id"], "music")
                fbArtistList = []
                fbArtistListString = ''
                if musicLikes['data'] != []:
                    for artist in musicLikes['data']:
                        if artist['category'] == "Musician/band":
                            fbArtistList.append(artist['name'])
                            fbArtistListString = fbArtistListString + artist['name'] + '<br/>'
                
                friendsData = graph.get_connections(userProfile["id"], "friends")
                friendIDs = []
                for index, friend in enumerate(friendsData['data']):
                    friendIDs.append(friend['id'])
                friendsProfileData = graph.Batch_Profile_Request(friendIDs)
                friendsMusicLikesData = graph.Batch_Music_Likes_Request(friendIDs)
                friendsProfileAndLikes = []
                for friendID in friendsProfileData:
                    profile = {}
                    profile['name'] = friendsProfileData[friendID]['name']
                    profile['url'] = friendsProfileData[friendID]['url']
                    profile['id'] = friendsProfileData[friendID]['id']
                    profile['music likes'] = friendsMusicLikesData[friendID]
                    friendsProfileAndLikes.append(profile)
                
                friendsString = '<br/><hr/>'   
                for friend in friendsProfileAndLikes:
                    friendMusicLikes = friend['music likes']
                    friendsString = friendsString + friend["name"]
                    friendsString = friendsString + '<br/><a href="' + friend["url"] + '">'
                    friendsString = friendsString + '<img src="http://graph.facebook.com/' + friend['id'] + '/picture?type=square"/></a><br/>'
                    if friendMusicLikes != []:
                        for artist in friendMusicLikes:
                            friendsString = friendsString + artist + '<br/>'
                    friendsString = friendsString + '<hr/>'

                user = models.FacebookUser(key_name = userProfile["id"],
                                           name = userProfile["name"],
                                           profile_url = userProfile["link"],
                                           access_token = cookie["access_token"],
                                           friendsJsonData = json.dumps(friendsProfileAndLikes),
                                           friendsString = friendsString)
                
                if fbArtistList != []:
                    user.fbArtistList = fbArtistList
                    user.fbArtistListString = fbArtistListString
                user.put()
                self._current_user = user
                
        return self._current_user
""" --- """


""" This Handler is responsible for displaying the HTML for the home
    page based on whether or not there is a user logged in"""
class HomeHandler(BaseHandler):
    def get(self):
      tmpl = path.join(path.dirname(__file__), "index.html")
      args = dict(current_user=self.current_user,
                    facebook_app_id=FACEBOOK_APP_ID)
      html = render(tmpl, args)
      self.response.out.write(html)
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/', HomeHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
