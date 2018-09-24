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
import os
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
import DataModels as models
from google.appengine.ext.webapp import template
import urllib

import wsgiref.handlers


# Makes the tags defined by templatetags/basetags.py usable
# by templates rendered in this file
#template.register_template_library('templatetags.basetags')


class BioWorkBaseHandler(webapp.RequestHandler):
    """Base Bio Work RequestHandlers with some convenience functions."""

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


class BioFindArtist(BioWorkBaseHandler):
    """Handler for listing albums."""

    def get(self):
        """Lists all available albums."""
        artists = models.ArtistBios.all().order('+artistName')
        self.render_to_response('biowork.html', {
          'artists': artists,
        })


class BioRedirect(BioWorkBaseHandler):
    """Handler for images replacing and deleting."""
    def post(self):
        user = users.get_current_user()
        #userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/biowork')
        
        actionMsg = ''
        bio = ''
        if self.request.get('bioTxt'):
            bioTxt = self.request.get('bioTxt')
            bioUrl = self.request.get('bioUrl')
            artistName = self.request.get('artist')

            bioFile = models.ArtistBios.get_or_insert(key_name = str(artistName), artistName = artistName)
            if bioFile:
                bioFile.artistBio = bioTxt
                bioFile.artistURL  = bioUrl
                bioFile.put()
                
                bioPage = db.GqlQuery("SELECT * FROM ArtistBios WHERE artistName = :1 LIMIT 1",
                                      artistName).fetch(1)
                if bioPage:
                    bio = bioPage[0].artistBio
                    bioUrl = bioPage[0].artistURL
                else:
                    bioJson = models.GetArtistBio(urllib.unquote_plus(artistName))
                    if bioJson['bios'].has_key('wikipedia'):
                        bio = bioJson['bios']['wikipedia']['text']
                        bio = models.ChkTxtEnc(bio)
                        bioUrl = bioJson['bios']['wikipedia']['url']
                    elif bioJson['bios'].has_key('last.fm'):
                        bio = bioJson['bios']['last.fm']['text']
                        bio = models.ChkTxtEnc(bio)
                        bioUrl = bioJson['bios']['last.fm']['url']
                    else:
                        bio = ''
                        bioUrl = ''
            else:
                actionMsg = 'Could Not Find bio DB entry'
                artistName = ''
                bio = ''
                bioUrl = ''

            self.render_to_response('biowork.html', {
                'currAction': actionMsg,
                'user' : user,
                'logoutUrl' : logoutUrl,
                'query': urllib.unquote_plus(artistName),
                'queryenc': artistName,
                'bio': bio,
                'bioUrl': bioUrl,
              })

        else:
            actionMsg = 'Error with data calls'
            self.response.out.write(actionMsg)


class BioWork(BioWorkBaseHandler):
    """Handler for searching pictures by tag."""
    def get(self, q):
        """Displays the tag search box and possibly a list of results."""
        user = users.get_current_user()
        #userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/biowork')
        
        query = self.request.get('q')
        queryenc = query.encode('utf-8')
        queryenc = urllib.quote_plus(queryenc)
        bio = ''
        bioUrl = ''
        if query:
            # ListProperty magically does want we want: search for the occurrence
            # of the term in any of the tags.
            #pics = ArtistImages.all().filter('artistName =', query)
            bioPage = db.GqlQuery("SELECT * FROM ArtistBios WHERE artistName = :1 LIMIT 1",
            queryenc).fetch(1)
            if bioPage:
                bio = bioPage[0].artistBio
                bioUrl = bioPage[0].artistURL
            else:
                bioJson = models.GetArtistBio(query)
                if bioJson['bios'].has_key('wikipedia'):
                    bio = bioJson['bios']['wikipedia']['text']
                    bio = models.ChkTxtEnc(bio)
                    bioUrl = bioJson['bios']['wikipedia']['url']
                elif bioJson['bios'].has_key('last.fm'):
                    bio = bioJson['bios']['last.fm']['text'].decode('utf-8')
                    bio = models.ChkTxtEnc(bio)
                    bioUrl = bioJson['bios']['last.fm']['url']
                else:
                    bio = ''
                    bioUrl = ''  
        else:
            query = ''
            
        self.render_to_response('biowork.html', {
            'currAction': '',
            'user' : user,
            'logoutUrl' : logoutUrl,
            'query': query,
            'queryenc': queryenc,
            'bio': bio,
            'bioUrl': bioUrl,
          })



#application = webapp.WSGIApplication([('/artist/biowork(.*)', BioWork),],
#                                       debug=True)

def main():
    url_map = [('/artist/biowork(.*)', BioWork),
               ('/artist/bioredirect', BioRedirect),
               ('/artist/biosearch', BioWork)]
    application = webapp.WSGIApplication(url_map,
                                         debug=True)  
    wsgiref.handlers.CGIHandler().run(application)
    #util.run_wsgi_app(application)

    
if __name__ == '__main__':
    main()
