""" This handler is responsible for creating Json document with links
    to our own internal API links for the other handlers for the app
    http://backendgroovebug.appspot.com/v1/magazine?artist=&user="""



import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from os import path
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import urllib2, urllib, datetime, facebook
 


""" Class that handles magazine requests"""
class BackgroundHandler(webapp.RequestHandler):
    def get(self, artist):
        facebookId = self.request.get('id')
        auth_token = self.request.get('fbauth')
        finalPreJson = {}
        finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'facebook id' : facebookId}
        finalPreJson['images'] = []

        graph = facebook.GraphAPI(auth_token)
        photoAlbums = graph.get_connections(facebookId, "albums")
        coverPhotosID = None
        for album in photoAlbums['data']:
            if album['name'] == 'Cover Photos':
                coverPhotosID = album['id']
        if coverPhotosID is not None:
            coverPhotosData = graph.get_connections(coverPhotosID, "photos")
            for picture in coverPhotosData['data']:
                backgroundEntry = {}
                backgroundEntry['url'] = picture['images'][0]['source']
                backgroundEntry['reduced'] = picture['images'][0]['source']
                backgroundEntry['license'] = {}
                backgroundEntry['license']['thumbnail'] = 'http://backendgroovebug.appspot.com/htmlimages/missing_profile_icon.png'
                finalPreJson['images'].append(backgroundEntry)

        if finalPreJson['images'] == []:
            backgroundEntry = {}
            backgroundEntry['url'] = 'http://' + str(hostUrl) + '/v2/static/images/FriendBackground.jpg'
            backgroundEntry['reduced'] = 'http://' + str(hostUrl) + '/v2/static/images/FriendBackground.jpg'
            backgroundEntry['license'] = {}
            backgroundEntry['license']['thumbnail'] = 'http://backendgroovebug.appspot.com/htmlimages/missing_profile_icon.png'
            finalPreJson['images'].append(backgroundEntry)

## Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(finalPreJson))
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v2/fbfriendbackgrounds(.*)', BackgroundHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
