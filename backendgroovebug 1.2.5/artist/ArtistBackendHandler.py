""" This Handler is responsible for logging the user in to the
    artist backend and view the different 'work' handlers"""


from __future__ import with_statement
import os
from os import path
from google.appengine.api import users
from google.appengine.ext import db, webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
from google.appengine.api import files, images, memcache
import DataModels as models
import urllib2, urllib, re

if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']



class ArtistBackendHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        baseUrl = 'http://' + str(hostUrl) + '/artist/'
        urlsWithNames = []
        urlsWithNames.append({'url' : baseUrl + 'statwork', 'name' : 'Statistics'})
        urlsWithNames.append({'url' : baseUrl + 'blobwork', 'name' : 'Blobs'})
        urlsWithNames.append({'url' : baseUrl + 'imagework', 'name' : 'Images'})
        urlsWithNames.append({'url' : baseUrl + 'biowork', 'name' : 'Bios'})
        urlsWithNames.append({'url' : baseUrl + 'videowork', 'name' : 'Videos'})
        urlsWithNames.append({'url' : baseUrl + 'audiowork', 'name' : 'Audio'})
        urlsWithNames.append({'url' : baseUrl + 'composite-manager', 'name' : 'Composite pages'})
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/v1/artist')

        context = {'title' : 'Artist Backend Home',
                   'user' : userName,
                   'logoutUrl' : logoutUrl,
                   'urls' : urlsWithNames,}
        tmpl = path.join(path.dirname(__file__), 'ArtistBackendHTML.html')
        html = render(tmpl, context)
        self.response.out.write(html)


        
""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist', ArtistBackendHandler),],
                                     debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
