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
from django.utils import simplejson as json
from google.appengine.ext.webapp import template
import urllib2, urllib, datetime

import wsgiref.handlers


# Makes the tags defined by templatetags/basetags.py usable
# by templates rendered in this file
template.register_template_library('templatetags.basetags')


class FacebookStatWorkHandler(webapp.RequestHandler):
    """Handler for creating statistics."""
    def get(self, q):
        """Displays the tag search box and possibly a list of results."""
        user = users.get_current_user()
        #userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/facebookstatwork')
        
        totalUsers = 0
        
        userList = models.FacebookUser.gql("WHERE access_token  != :accessToken", accessToken = None)
        if userList != None:
            for user in userList:
                totalUsers += 1
        finalPreJson = {}
        finalPreJson['total facebook users'] = totalUsers
        facebookUserStatJson = json.dumps(finalPreJson, separators=(',',':'))
        

## Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(facebookUserStatJson)
      

def main():
    url_map = [('/artist/facebookstatwork', FacebookStatWorkHandler)]
    application = webapp.WSGIApplication(url_map,
                                         debug=True)  
    wsgiref.handlers.CGIHandler().run(application)
      #util.run_wsgi_app(application)

    
if __name__ == '__main__':
  main()
