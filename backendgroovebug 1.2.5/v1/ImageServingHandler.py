import os
from os import path
from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import users, files
from django.utils import simplejson as json
import DataModels as models
import urllib2, urllib, re



""" This Handler dynamically serves composite thumbnail images by looking
    up the thumbnail with the CompositePage ID provided in the wrapper.
    the wrapper for this handler is
    http://backendgroovebug.appspot.com/v1/compositethumbnails?imgid="""
class CompositeThumbnailHandler(webapp.RequestHandler):
    def get(self, imgid):
        imgid = self.request.get("imgid")
        if imgid:
            imgid = int(imgid)
            compositePage = models.CompositePage.get_by_id(imgid)
              
            if compositePage.thumbnail:
                self.response.headers['Content-Type'] = "image/png"
                self.response.out.write(compositePage.thumbnail)
            else:
                self.response.out.write('Not Here!')
        else:
            self.response.out.write('Not Here!')
""" --- """



""" Main function which handles url mappings"""
application = webapp.WSGIApplication([('/v1/thumbnailscomposite(.*)', CompositeThumbnailHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
