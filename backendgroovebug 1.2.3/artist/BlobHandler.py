""" This Handler is responsible for making the API calls to echonest, parsing the
    json data for a given artist, creating our own html document for artist bio
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/bio?artist="""



import os
from os import path
from google.appengine.ext import db, webapp, deferred
from google.appengine.ext import blobstore
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
from google.appengine.api import images
import urllib2, urllib, datetime, re, htmlentitydefs
from google.appengine.runtime import DeadlineExceededError
import DataModels as models


#class DeleteBlobs(webapp.RequestHandler):

#def post(self, delCnt):
def deleteBlobs(delCnt):
    #delCnt = self.request.get('delCnt')
    allBlobs = blobstore.BlobInfo.all();
    allCnt = allBlobs.count()
    blobChkCnt = 0
    currDeleted = 0
    
    for blobEntry in allBlobs:
        blobFound = False
        urlChk = images.get_serving_url(blobEntry.key())
        #return blobEntry.key()
        
        blobChk = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistImgUrl = :1 LIMIT 1",
      urlChk).fetch(1)
        if len(blobChk) > 0:
            blobFound = True
            name = blobChk[0].artistName
        else:
            blobChk = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistThmbUrl = :1 LIMIT 1",
          urlChk).fetch(1)
            if len(blobChk) > 0:
                blobFound = True
                name = blobChk[0].artistName
            else:
                blobChk = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistReducedImgUrl = :1 LIMIT 1",
              urlChk).fetch(1)
                if len(blobChk) > 0:
                    blobFound = True
                    name = blobChk[0].artistName
                else:
                    blobChk = db.GqlQuery("SELECT * FROM PromotedAudio WHERE blobKey = :1 LIMIT 1", str(blobEntry.key())).fetch(1)
                    if len(blobChk) > 0:
                        blobFound = True
                        name = blobChk[0].artistName
                    else:
                        blobChk = db.GqlQuery("SELECT * FROM PromotedAudio WHERE imgBlobkey = :1 LIMIT 1", str(blobEntry.key())).fetch(1)
                        if len(blobChk) > 0:
                            blobFound = True
                            name = blobChk[0].artistName
                        else:
                            blobChk = db.GqlQuery("SELECT * FROM PromotedAudio WHERE thumbBlobkey = :1 LIMIT 1", str(blobEntry.key())).fetch(1)
                            if len(blobChk) > 0:
                                blobFound = True
                                name = blobChk[0].artistName
                            else:
                                blobChk = db.GqlQuery("SELECT * FROM CompositePage WHERE graphicBlobKey = :1 LIMIT 1", str(blobEntry.key())).fetch(1)
                                if len(blobChk) > 0:
                                    blobFound = True
                                    name = blobChk[0].title
                                else:
                                    blobChk = db.GqlQuery("SELECT * FROM CompositePage WHERE thumbnailBlobKey = :1 LIMIT 1", str(blobEntry.key())).fetch(1)
                                    if len(blobChk) > 0:
                                        blobFound = True
                                        name = blobChk[0].title
                    
        blobChkCnt += 1
        if blobFound:
            strRet = '#' + str(blobChkCnt) + ': ' + urlChk + ' found in artist images. Artist is ' + name
            #return strRet
        else:
            #blobEntry.delete()
            currDeleted += 1
            strRet = '#' + str(blobChkCnt) + ': ' + str(blobEntry.key()) + ' not found in artist images or promoted audio. Blob deleted'
            return strRet
        
        if currDeleted >= delCnt:
            break

    strRet = str(blobChkCnt) + ' records checked. ' + str(currDeleted) + ' records deleted.' 
    return strRet

        
""" Class that handles biography requests"""
class BlobHandler(webapp.RequestHandler):
    def get(self, action):
        blobData = 'Nothing done yet'
        bAction = self.request.get("action")
        
        if bAction == 'delete':

            #taskqueue.add(url='/artist/blobdelete', params={'delCnt': 100})

            #self.redirect('/v1/blobwork(.*)')

            ## Use HandleBlob method to handle actions to the Blobstore
            blobData = deleteBlobs(100)
        else:
            blobData = 'Please choose an appropriate action'

        # Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(blobData)

""" --- """




""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist/blobwork(.*)', BlobHandler),
                                      ('/artist/blobdelete(.*)', deleteBlobs)],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
