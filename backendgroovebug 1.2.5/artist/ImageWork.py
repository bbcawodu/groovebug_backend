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
import DataModels as models
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
from google.appengine.ext.webapp import template
import urllib2, urllib, datetime
from datetime import tzinfo, timedelta, datetime

import wsgiref.handlers


# Makes the tags defined by templatetags/basetags.py usable
# by templates rendered in this file
#template.register_template_library('templatetags.basetags')


class ImageWorkBaseHandler(webapp.RequestHandler):
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


class ImageFindArtist(ImageWorkBaseHandler):
    """Handler for listing albums."""

    def get(self):
        """Lists all available albums."""
        artists = ArtistImages.all().order('+artistName')
        self.render_to_response('index.html', {
          'artists': artists,
        })


class ImageSharingAlbumCreate(ImageWorkBaseHandler):
    """Handler for creating a new Album via form."""

    def get(self):
        """Displays the album creation form."""
        self.render_to_response('new.html', {})

    def post(self):
        """Processes an album creation request."""
        Album(name=cgi.escape(self.request.get('albumname')),
              creator=users.get_current_user()).put()
        self.redirect('/')

PICTURES_PER_ROW = 5


class ImageSharingShowImage(ImageWorkBaseHandler):
    """Handler for viewing a single image.

    Note that this doesn't actually serve the picture, only the page
    containing it. That happens in ImageSharingServeImage.
    """

    def get(self, pic_key):
        """Renders the page for a single picture.

        Args:
          pic_key: key for the Picture model for the picture to display
        """

        pic = db.get(pic_key)
        self.render_to_response('show_image.html', {
            'pic': pic,
            'image_key': pic.key(),
        })


def updateMemCache(artistName, pics):
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0'}
    finalPreJson['images'] = []

    for img in pics:
        if img.artistReducedImgUrl:
            if img.artistReducedImgUrl != '':
                tempReduced = img.artistReducedImgUrl
            else:
                tempReduced = img.artistImgUrl
        else:
            tempReduced = img.artistImgUrl

        if img.artistImgLicense:
            if img.artistImgLicense == {}:
                tempLic = {"url": "", "attribution": "", "type": "unknown", 'thumbnail' : img.artistThmbUrl}
            elif img.artistImgLicense == '':
                tempLic = {"url": "", "attribution": "", "type": "unknown", 'thumbnail' : img.artistThmbUrl}
            else:
                tempLic = img.artistImgLicense
                tempLic['thumbnail'] = img.artistThmbUrl

        else:
            tempLic = {"url": "", "attribution": "", "type": "unknown", 'thumbnail' : img.artistThmbUrl}
                
        backUrlAdd = {'url' : img.artistImgUrl,
                      'reduced' : tempReduced,
                      'license' : tempLic}
        
        finalPreJson['images'].append(backUrlAdd)

    data = memcache.get('artistImages' + artistName)
    if data is not None:
        memcache.set('artistImages' + artistName, finalPreJson['images'], 604800)
    else:
        memcache.add('artistImages' + artistName, finalPreJson['images'], 604800)



class ImageRedirect(ImageWorkBaseHandler):
    """Handler for images replacing and deleting."""
    def post(self):
        user = users.get_current_user()
        #userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/imagework')
        
        actionCompl = False
        actionMsg = ''
        if self.request.get('deleteImage'):
            imgKey = self.request.get('deleteImage')
            imgFile = db.get(imgKey)
            if imgFile:
                artistName = imgFile.artistName
                queryName = artistName.encode('utf-8')
                queryName = urllib.quote_plus(queryName)
                
                actionMsg = DeleteImages(imgFile)
                actionCompl = True
                pics = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 100",
                         artistName).fetch(20)

                updateMemCache(artistName, pics)
                self.redirect('/artist/imagework?q=' + artistName + '&actionMsg=' + actionMsg)
            else:
                actionMsg = 'Could Not Find Image DB entry'
                artistName = ''
                pics = []

            if actionMsg == '':
                actionMsg = 'Searching by Artist'

            self.render_to_response('imgsearch.html', {
                'currAction': actionMsg,
                'user' : user,
                'logoutUrl' : logoutUrl,
                'query': artistName,
                'pics': pics,
              })

        elif self.request.get('replaceImage'):
            imgKey = self.request.get('replaceImage')
            imgFile = db.get(imgKey)
            if imgFile:
                artistName = imgFile.artistName
                queryName = artistName.encode('utf-8')
                queryName = urllib.quote_plus(queryName)

                if self.request.get('replace'):
                    replImage = self.request.get('replace')
                    imgFile.artistOrigImgUrl = 'Manually Replaced'
                    #imgFile.put
                    actionMsg = UpdateArtistImages(imgFile, replImage)
                    pics = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 100",
                         artistName).fetch(20)
                    
                    if actionMsg == 'Completed':
                        actionMsg = 'Image Replaced!!!'
                        updateMemCache(artistName, pics)
                        self.redirect('/artist/imagework?q=' + artistName + '&actionMsg=' + actionMsg)
                else:
                    actionMsg = 'You have not selected an image'
                    pics = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 100",
                             artistName).fetch(20)
                
            else:
                actionMsg = 'Could Not Find Image DB entry'
                artistName = ''
                pics = []

            if actionMsg == '':
                actionMsg = 'Searching by Artist'

            self.render_to_response('imgsearch.html', {
                'currAction': actionMsg,
                'user' : user,
                'logoutUrl' : logoutUrl,
                'query': urllib.unquote_plus(artistName),
                'pics': pics,
              })

        elif self.request.get('addImage'):
            artistName = self.request.get('addImage')
            queryName = artistName.encode('utf-8')
            queryName = urllib.quote_plus(queryName)
            if queryName != '':
                if self.request.get('add'):
                    imgToAdd = self.request.get('add')
                    
                    imgFile = models.ArtistImages(artistName = queryName)
                    imgFile.artistOrigImgUrl = 'Manually Added'
                    #imgFile.put
                    actionMsg = UpdateArtistImages(imgFile, imgToAdd)
                    pics = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 100",
                             queryName).fetch(20)
                    if actionMsg == 'Completed':
                        actionMsg = 'Image Added!!!'
                        updateMemCache(queryName, pics)
                        self.redirect('/artist/imagework?q=' + queryName + '&actionMsg=' + actionMsg)
                else:
                    actionMsg = 'You have not selected an image'
                    pics = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 100",
                             queryName).fetch(20) 
            else:
                actionMsg = 'There is no artist name'
                artistName = ''
                pics = []

            if actionMsg == '':
                actionMsg = 'Searching by Artist'

            self.render_to_response('imgsearch.html', {
                'currAction': actionMsg,
                'user' : user,
                'logoutUrl' : logoutUrl,
                'query': artistName,
                'pics': pics,
              })
        else:
            actionMsg = 'Error with data calls'

def DeleteImages(imgFile):
    actionMsg = ''
    artistName = imgFile.artistName
    queryName = artistName.encode('utf-8')
    queryName = urllib.quote_plus(queryName)

    try:
        if imgFile.artistReducedImgUrl:
            if imgFile.artistReducedImgUrl != '':
                if imgFile.artistReducedImgBlobKey:
                    if imgFile.artistReducedImgBlobKey != '':
                        blobstore.delete(imgFile.artistReducedImgBlobKey)
                        imgFile.artistReducedImgUrl = ''
                        imgFile.put()

        if imgFile.artistImgUrl:
            if imgFile.artistImgUrl != '':
                if imgFile.artistImgBlobKey:
                    if imgFile.artistImgBlobKey != '':
                        blobstore.delete(imgFile.artistImgBlobKey)
                        imgFile.artistImgUrl = ''
                        imgFile.put()
            else:
                actionMsg = 'Empty Image URL'

        else:
            actionMsg = 'Image URL Is Missing'
            
        if imgFile.artistThmbUrl:
            if imgFile.artistThmbUrl != '':
                if imgFile.artistThmbBlobKey:
                    if imgFile.artistThmbBlobKey != '':
                        blobstore.delete(imgFile.artistThmbBlobKey)
                        imgFile.artistThmbUrl = ''
                        imgFile.put()
            else:
                actionMsg = 'Empty Thumbnail URL'

        else:
            actionMsg = 'Thumbnail URL Is Missing'
              
        imgFile.delete()
        actionMsg = 'Image Deleted!!!'
    except Exception, error:
        actionMsg = error

    return actionMsg
    
def UpdateArtistImages(imgFile, uImg):
    minWidth = 300
    minHeight = 300
    maxImpWidth = 1200
    maxImpHeight = 1200
    maxWidth = 800
    maxHeight = 600
    actionMsg = ''

    artistName = imgFile.artistName

    imgFile.artistImg = db.Blob(uImg)
    
    try:
        imgW = images.Image(imgFile.artistImg).width
        imgFile.artistImgWidth = imgW 
        imgH = images.Image(imgFile.artistImg).height
        imgFile.artistImgHeight = imgH
        scaleW = imgW
        scaleH = imgH
        if ((maxImpWidth + 1) > imgW > (minWidth - 1)) and ((maxImpHeight + 1) > imgH > (minHeight -1)):

#       Write the image to the blobstore
            imgFile.artistImg = images.resize(imgFile.artistImg, imgW, imgH, output_encoding=images.JPEG)
             # Create the Blob file
            file_name = files.blobstore.create(mime_type='image/jpeg')
             # Open the file and write to it
            with files.open(file_name, 'a') as f:
                f.write(imgFile.artistImg)
             # Finalize the file. Do this before attempting to read it.
            files.finalize(file_name)
             # Get the file's blob key
            imgBlobKey = files.blobstore.get_blob_key(file_name)
            oldBlobKey = imgFile.artistImgBlobKey
            if oldBlobKey:
                if oldBlobKey != '':
                    blobstore.delete(oldBlobKey)
                
            imgFile.artistImgBlobKey = str(imgBlobKey)
            imgFile.artistImgUrl = images.get_serving_url(imgBlobKey)
            imgFile.artistImgLicense = {"url": imgFile.artistImgUrl, "attribution": "", "type": imgFile.artistOrigImgUrl}

            if imgFile.artistReducedImgBlobKey:
                oldBlobKey = imgFile.artistReducedImgBlobKey
                if oldBlobKey != '':
                    blobstore.delete(oldBlobKey)
            else:
                oldBlobKey = ''

            imgFile.artistReducedImgBlobKey = None
            imgFile.artistReducedImgUrl = None
            imgFile.artistReducedImg = None
            imgFile.artistReducedImgWidth = None
            imgFile.artistReducedImgHeight = None

#        if the image is bigger than a certain size resize it and write the image to the blobstore             
            if (imgW > maxWidth) or (imgH > maxHeight):
                imgR = float(imgW) / float(imgH)
                maxR = float(maxWidth) / float(maxHeight)
                if imgR < maxR:
                    scaleH = maxHeight
                    scaleW = (maxHeight * imgW)/imgH
                else:
                    scaleH = (maxWidth * imgH)/imgW
                    scaleW = maxWidth
                   
                tmpImg = images.resize(imgFile.artistImg, scaleW, scaleH, output_encoding=images.JPEG)
                imgFile.artistReducedImg = db.Blob(tmpImg)
                imgFile.artistReducedImgWidth = images.Image(imgFile.artistReducedImg).width
                imgFile.artistReducedImgHeight = images.Image(imgFile.artistReducedImg).height
            
                 # Create the Blob file
                file_name = files.blobstore.create(mime_type='image/jpeg')
                 # Open the file and write to it
                with files.open(file_name, 'a') as f:
                    f.write(imgFile.artistReducedImg)
                 # Finalize the file. Do this before attempting to read it.
                files.finalize(file_name)
                 # Get the file's blob key
                imgBlobKey = files.blobstore.get_blob_key(file_name)
                imgFile.artistReducedImgBlobKey = str(imgBlobKey)
                imgFile.artistReducedImgUrl = images.get_serving_url(imgBlobKey)


#            Size the image to a thumbnail and write the thumbnail to the blobstore
            if imgW > imgH:
                imgThmbW = (imgW * 100)/imgH
                tmpThmb = images.resize(imgFile.artistImg, imgThmbW, 100, output_encoding=images.JPEG)
                ThmbW = images.Image(tmpThmb).width
                cLeft = float(((ThmbW - 100.0)/2.0)/ThmbW)
                cTop = 0.0
                cRight = float((ThmbW - ((ThmbW - 100.0)/2.0))/ThmbW)
                cBottom = 1.0
                tmpThmbCrop = images.crop(tmpThmb, cLeft, cTop, cRight, cBottom, output_encoding=images.JPEG)
                ThmbW = images.Image(tmpThmbCrop).width
                imgFile.artistThmb = db.Blob(tmpThmbCrop)
        
            else:
                imgThmbH = (imgH * 100)/imgW
                tmpThmb = images.resize(imgFile.artistImg, 100, imgThmbH, output_encoding=images.JPEG)
                ThmbH = images.Image(tmpThmb).height
                cLeft = 0.0
                cTop = 0.0
                cRight = 1.0
                cBottom = float(100.0/ThmbH)
                tmpThmbCrop = images.crop(tmpThmb, cLeft, cTop, cRight, cBottom, output_encoding=images.JPEG)
                ThmbH = images.Image(tmpThmbCrop).height
                imgFile.artistThmb = db.Blob(tmpThmbCrop)

             # Create the Blob file
            file_name = files.blobstore.create(mime_type='image/jpeg')
             # Open the file and write to it
            with files.open(file_name, 'a') as f:
                f.write(imgFile.artistThmb)
            
            # Finalize the file. Do this before attempting to read it.
            files.finalize(file_name)
        
            # Get the file's blob key
            imgBlobKey = files.blobstore.get_blob_key(file_name)
            oldBlobKey = imgFile.artistThmbBlobKey
            if oldBlobKey:
                if oldBlobKey != '':
                    blobstore.delete(oldBlobKey)

            imgFile.artistThmbBlobKey = str(imgBlobKey)
            imgFile.artistThmbUrl = images.get_serving_url(imgBlobKey)
            imgFile.dateAdded = datetime.utcnow().date()

            imgFile.put()

            actionMsg = 'Completed'
        else:
            if imgW < minWidth or imgH < minHeight:
                actionMsg = 'Image is too small'
            else:
                actionMsg = 'Image is too big'

    except Exception, error:
        actionMsg = error

    return actionMsg  

class ImageWork(ImageWorkBaseHandler):
    """Handler for searching pictures by tag."""
    def get(self, q):
        """Displays the tag search box and possibly a list of results."""
        user = users.get_current_user()
        #userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/imagework')

        query = self.request.get('q')
        queryenc = query.encode('utf-8')
        queryenc = urllib.quote_plus(queryenc)
        actionMsg = self.request.get('actionMsg')
        if not actionMsg:
            actionMsg = 'Searching by Artist'
        pics = []
        if query:
            # ListProperty magically does want we want: search for the occurrence
            # of the term in any of the tags.
            pics = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 100",
            queryenc).fetch(20)
        else:
            query = ''
            
        self.render_to_response('imgsearch.html', {
            'currAction': actionMsg,
            'user' : user,
            'logoutUrl' : logoutUrl,
            'query': query,
            'pics': pics,
          })



#application = webapp.WSGIApplication([('/artist/imagework(.*)', ImageWork),],
#                                       debug=True)

def main():
    url_map = [('/artist/imagework(.*)', ImageWork),
               ('/artist/imageredirect', ImageRedirect),
               ('/artist/search', ImageWork)]
    application = webapp.WSGIApplication(url_map,
                                         debug=True)  
    wsgiref.handlers.CGIHandler().run(application)
      #util.run_wsgi_app(application)

    
if __name__ == '__main__':
  main()
