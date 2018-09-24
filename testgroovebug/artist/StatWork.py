#!/usr/bin/python2.5
#
# Copyright 2008 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import with_statement
import cgi
## Change settings to the 'settings' file within backend directory
import os
from os import path
from google.appengine.api import images, memcache
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.api import files
from operator import itemgetter, attrgetter
import DataModels as models
from google.appengine.ext.webapp import util
import json
from google.appengine.ext.webapp import template
import urllib2, urllib, datetime

import wsgiref.handlers


# Makes the tags defined by templatetags/basetags.py usable
# by templates rendered in this file
#template.register_template_library('templatetags.basetags')


class StatWorkBaseHandler(webapp.RequestHandler):
    """Base Image Sharing RequestHandlers with some convenience functions."""

    def template_path(self, filename):
        """Returns the full path for a template from its path relative to here."""
        #return os.path.join(os.path.dirname(__file__), 'templates/html/' + filename)
        return os.path.join(os.path.dirname(__file__), filename)

    def render_to_response(self, filename, template_args):
        """Renders a Django template and sends it to the client.

        Args:
        filename: template path (relative to this file)
        template_args: argument dict for the template
        """
        template_args.setdefault('current_uri', self.request.uri)
        self.response.out.write(
          template.render(self.template_path(filename), template_args)
        )



class StatWork(StatWorkBaseHandler):
    """Handler for creating statistics."""
    def get(self, q):
        """Displays the tag search box and possibly a list of results."""
        user = users.get_current_user()
        #userName = user.nickname()
        logoutUrl = users.create_logout_url('/v1/imagework')
        
        offset = 0
        fetchamt = 100
        artistTotals = {}
        
        UserList = db.GqlQuery("SELECT * FROM GroovebugUser").fetch(limit=fetchamt, offset=offset)
        artistTotals['00 Total Artists'] = 0
        for userEntry in UserList:
            libList = userEntry.artistList
            for libEntry in libList:
                if artistTotals.has_key(libEntry):
                    artistTotals[libEntry] += 1
                else:
                    artistTotals[libEntry] = 1
                    artistTotals['00 Total Artists'] += 1

        sortedArtistTotals = sorted(artistTotals.items(), key=lambda t: t[0].lower())
        artistStatJson = json.dumps(sortedArtistTotals, separators=(',',':'))
        

## Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(artistStatJson)


        

def main():
    url_map = [('/artist/statwork(.*)', StatWork)]
    application = webapp.WSGIApplication(url_map,
                                         debug=True)  
    wsgiref.handlers.CGIHandler().run(application)
      #util.run_wsgi_app(application)

    
if __name__ == '__main__':
  main()
