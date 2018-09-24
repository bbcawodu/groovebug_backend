""" This Handler is responsible for making the API calls to youtube, parsing the
    json data for a given artist, creating a formatted HTML document with youtube
    video links, and returning it when queried using our internal API
    the wrapper for videos will be
    http://backendgroovebug.appspot.com/v1/videos?artist="""


from __future__ import with_statement
from os import path
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import files, images
import DataModels as models
import urllib



""" This function recieves an artist name as an input and outputs an array of dictionaries
    which contain a title, video link, and thumbnail link. There is an optional second
    argument for the max amount of entries in the array, default is 20."""
def GetArtistVideos(artist, maxResults = 20):
## Encode results into unicode which can be parsed by iTunes API
    artist = artist.encode('utf-8')
    artistName = urllib.quote_plus(artist)
## Initialize list that will contain dictionary entries with video data
    videos = []
    ExclList = []
    PromoList = []
    PromoSetList = []
    VidRec = db.GqlQuery("SELECT * FROM ArtistVideos WHERE artistName = :1 LIMIT 1",
                           artistName).fetch(1)
    if len(VidRec) > 0:
        ExclList = VidRec[0].videosToExclude
        PromoList = VidRec[0].videosToPromote
        #return PromoList
        if ExclList:
            if len(ExclList) > 0:
                maxResults = maxResults + len(ExclList)
                if maxResults > 50:
                    maxResults = 50
        else:
            ExclList = []

        PromoSetList = []
        if PromoList:
            if len(PromoList) > 0:
                for entry in PromoList:
                    PromoSetList.append(entry['link'])
            else:
                PromoList = []
        else:
            PromoList = []
            
    ExclSet = set(ExclList)
    PromoSet = set(PromoSetList)

## Populate videos list with promo videos dictionary entries with "title", "thumbnail", and video link data           
    for entry in PromoList:
        if entry['link'] not in ExclSet:
            video = {}
            video['title'] = entry['title']
            video['thumb'] = entry['thumb']
            video['link'] = entry['link']
            video['promoted'] = True
            videos.append(video)
    
## Obtain Json text for specified artist from youtube
    searchBase = 'http://gdata.youtube.com/feeds/api/videos?'
    searchArgs = {'alt' : 'json',
                  'q' : "\"" + artist + "\"",
                  'key' : 'AI39si4valAWDvFNMsZCFKWydGjC9yMHhMmSvQ_lHINbx8dA1oWUinsFSLfRoBc7ojrynjN65ZBqogEjStplkSPfPfvQ-1n_rw',
                  'max-results' : maxResults,
                  'category' : 'Music',
                  'format' : '6',}
    url = str(searchBase) + urllib.urlencode(searchArgs)
    
# Try loading Json doc from URL, if loading times out, try again up to
# 'maxLookupRetry' times
    artistJson = models.RetryLoadJson(url)
    if artistJson == []:
        errorMessage = 'The YouTube API request timed out'
        return errorMessage
    
    videoJson = artistJson['feed']

## Returns empty videos list if videos for artist are not found on youtube 
    if not videoJson.has_key('entry'):
        return videos

            
## Populate videos list with dictionary entries with "title", "thumbnail", and video link data
    artistDict = videoJson['entry']
            
    for entry in artistDict:
        if entry['link'][0]['href'] not in ExclSet and entry['link'][0]['href'] not in PromoSet:
            video = {}
            video['title'] = entry['title']['$t']
            video['thumb'] = entry['media$group']['media$thumbnail'][0]['url']
            video['link'] = entry['link'][0]['href']
            video['promoted'] = False
            videos.append(video)

## Return populated videos list
    return videos
""" --- """



""" Class that handles video requests"""
class VideoWorkHandler(webapp.RequestHandler):
    def get(self, artist):
## Use GetArtistVideos method to obtain video data from youtube
        artist = self.request.get("artist")
        artistEnc = artist.encode('utf-8')
        artistEnc = urllib.quote_plus(artistEnc)

        if self.request.get("actionMsg"):
            actionMsg = self.request.get("actionMsg")
        else:
            actionMsg = ''
            
        videos = GetArtistVideos(artist)
        upload_url = blobstore.create_upload_url('/artist/videoaddredirect')
## If the Youtube API request timed out, display error message
        if videos == 'The YouTube API request timed out':
            context = {'error' : 'The YouTube API request timed out'}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# If there are no videos found on youtube for the artist, display error message
        elif not videos:
            if artist:
                context = {'error' : 'Sorry, there are no videos found on youtube for this artist', 'artist' : artist,
                           'artistEnc' : artistEnc, 'upload' : upload_url}
            else:
                context = {'error' : 'Please enter an artist to search for'}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# Otherwise, use video data to create html document
        else:
            if actionMsg != '':
                context = {'error' : actionMsg, 'videos' : videos, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            else:
                context = {'videos' : videos, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
""" --- """

""" Class that handles video requests"""
class VideoWorkRedirect(webapp.RequestHandler):
    def post(self, artist):
        artist = self.request.get('artistName')
        artistEnc = self.request.get('artistEnc')
        actionMsg = ''

        unPromoList = self.request.get_all('unpromote')
        if unPromoList:
            if not len(unPromoList) > 0:
                unPromoList = []
        
        PromoList = self.request.get_all('promote')
        if PromoList:
            if not len(PromoList) > 0:
                PromoList = []
                                              
        ExclList = self.request.get_all('exclude')
        if ExclList:
            if not len(ExclList) > 0:
                ExclList = []
                
        if len(unPromoList) > 0 or len(PromoList) > 0 or len(ExclList) > 0:
            videoFile = models.ArtistVideos.get_or_insert(key_name = artistEnc, artistName = artistEnc)
            if not videoFile.videosToPromote:
                videoFile.videosToPromote = []
            if not videoFile.videosToExclude:
                videoFile.videosToExclude = []

            if len(unPromoList) > 0:
                for entry in unPromoList:
                    for sEntry in videoFile.videosToPromote:
                        if entry == sEntry['link']:
                            if sEntry.has_key('blobkey'):
                                imgBlobKey = sEntry['blobkey']
                                if imgBlobKey:
                                    delFile = blobstore.BlobInfo.get(imgBlobKey)
                                    if delFile:
                                        delFile.delete()
                                    else:
                                        actionMsg = 'Image Blob not found'
                            videoFile.videosToPromote.remove(sEntry)

            if len(PromoList) > 0:
                for entry in PromoList:
                    vEntry = {}
                    getVal = 'title' + str(entry)
                    vEntry['title'] = str(self.request.get(getVal))
                    getVal = 'thumburl' + str(entry)
                    vEntry['thumb'] = self.request.get(getVal)
                    getVal = 'link' + str(entry)
                    vEntry['link'] = self.request.get(getVal)
                    videoFile.videosToPromote.append(vEntry)

            if len(ExclList) > 0:
                if videoFile.videosToExclude:
                    if len(videoFile.videosToExclude) > 0:
                        videoFile.videosToExclude.extend(ExclList)
                    else:
                        videoFile.videosToExclude = ExclList
                else:
                    videoFile.videosToExclude = ExclList

            videoFile.put()

## Use GetArtistVideos method to obtain video data from youtube
        videos = GetArtistVideos(artist)
        upload_url = blobstore.create_upload_url('/artist/videoaddredirect')
## If the Youtube API request timed out, display error message
        if videos == 'The YouTube API request timed out':
            context = {'error' : 'The YouTube API request timed out'}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# If there are no videos found on youtube for the artist, display error message
        elif not videos:
            context = {'error' : 'Sorry, there are no videos found on youtube for this artist', 'artist' : artist,
                       'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# Otherwise, use video data to create html document
        else:
            if actionMsg != '':
                context = {'error' : actionMsg, 'videos' : videos, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            else:
                context = {'videos' : videos, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
        


""" --- """

""" Class that handles video requests"""
class VideoAddRedirect(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, artist):
        artist = self.request.get('artistName')
        artistEnc = self.request.get('artistEnc')
        actionMsg = ''

        if self.request.get('addVideo'):
            if artistEnc != '':
                if not self.request.get('videotitle'):
                    actionMsg = 'You Need A Title To Add A Video'
                else:
                    vTitle = self.request.get('videotitle')
                    vTitle = vTitle.strip()
                    if vTitle == '':
                        actionMsg = 'You Need A Title To Add A Video'
                    else:
                        if not self.request.get('videourl'):
                            actionMsg = 'You Need A URL To Add A Video'
                        else:
                            vUrl = self.request.get('videourl')
                            vUrl = vUrl.strip()
                            if vUrl == '':
                                actionMsg = 'You Need A URL To Add A Video'
                            else:
                                if not self.request.get('videothumb'):
                                    actionMsg = 'You Need An Image To Add A Video'

            else:
                actionMsg = 'There Is No Artist To Add The Video To'

        if actionMsg == '':
            try:
                upload_files = self.get_uploads('videothumb')  # 'file' is file upload field in the form
                blob_info = upload_files[0]
                thmbBlobKey = blob_info.key()

                if thmbBlobKey:
                    videoFile = models.ArtistVideos.get_or_insert(key_name = artistEnc, artistName = artistEnc)
                    if not videoFile.videosToPromote:
                        videoFile.videosToPromote = []

                    if vUrl not in videoFile.videosToPromote:                   
                        imgJson = getVideoImageInfo(thmbBlobKey)
                        
                        if imgJson['actionMsg'] == 'Completed':
                            vEntry = {}
                            vEntry['title'] = vTitle
                            vEntry['link'] = vUrl
                            vEntry['thumb'] = imgJson['imgUrl']
                            vEntry['blobkey'] = str(thmbBlobKey)
                            videoFile.videosToPromote.append(vEntry)
                            videoFile.put()
                            actionMsg = 'Video Added'
                            self.redirect('/artist/videowork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
                        else:
                            actionMsg = imgJson['actionMsg']
                            self.response.out.write(actionMsg)
                            return 'ok'
                    else:
                        actionMsg = 'Video Already In Promoted List'

                else:
                    actionMsg = 'Problem With Uploading Image'

            except Exception, error:
                actionMsg = error
                self.response.out.write(actionMsg)
                return 'ok'
        else:
            self.redirect('/artist/videowork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
            
## Use GetArtistVideos method to obtain video data from youtube
        videos = GetArtistVideos(artist)
        upload_url = blobstore.create_upload_url('/artist/videoaddredirect')
## If the Youtube API request timed out, display error message
        if videos == 'The YouTube API request timed out':
            context = {'error' : 'The YouTube API request timed out'}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# If there are no videos found on youtube for the artist, display error message
        elif not videos:
            context = {'error' : 'Sorry, there are no videos found on youtube for this artist', 'artist' : artist,
                       'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# Otherwise, use video data to create html document
        else:
            if actionMsg != '':
                context = {'error' : actionMsg, 'videos' : videos, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            else:
                context = {'videos' : videos, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'videowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
        


""" --- """

def getVideoImageInfo(imgBlobKey, MakeThumb=False):
    imgReturn = {}
    
    try:
        blob_reader = blobstore.BlobReader(imgBlobKey)
        trkImg = blob_reader.read()
        imgW = images.Image(trkImg).width
        imgH = images.Image(trkImg).height
             
        imgUrl = images.get_serving_url(imgBlobKey)
        imgReturn['imgBlobKey'] = imgBlobKey
        imgReturn['imgUrl'] = imgUrl

        if MakeThumb:
        #Size the image to a thumbnail and write the thumbnail to the blobstore
            if imgW > imgH:
                imgThmbW = (imgW * 100)/imgH
                tmpThmb = images.resize(trkImg, imgThmbW, 100, output_encoding=images.JPEG)
                ThmbW = images.Image(tmpThmb).width
                cLeft = float(((ThmbW - 100.0)/2.0)/ThmbW)
                cTop = 0.0
                cRight = float((ThmbW - ((ThmbW - 100.0)/2.0))/ThmbW)
                cBottom = 1.0
                tmpThmbCrop = images.crop(tmpThmb, cLeft, cTop, cRight, cBottom, output_encoding=images.JPEG)
                ThmbW = images.Image(tmpThmbCrop).width    
            else:
                imgThmbH = (imgH * 100)/imgW
                tmpThmb = images.resize(trkImg, 100, imgThmbH, output_encoding=images.JPEG)
                ThmbH = images.Image(tmpThmb).height
                cLeft = 0.0
                cTop = 0.0
                cRight = 1.0
                cBottom = float(100.0/ThmbH)
                tmpThmbCrop = images.crop(tmpThmb, cLeft, cTop, cRight, cBottom, output_encoding=images.JPEG)
                ThmbH = images.Image(tmpThmbCrop).height

            # Create the Blob file
            file_name = files.blobstore.create(mime_type='image/jpeg')
            # Open the file and write to it
            with files.open(file_name, 'a') as f:
                f.write(tmpThmbCrop)
            
            # Finalize the file. Do this before attempting to read it.
            files.finalize(file_name)
        
            # Get the file's blob key
            thumbBlobKey = files.blobstore.get_blob_key(file_name)
            thumbUrl = images.get_serving_url(thumbBlobKey)

            imgReturn['thumbBlobKey'] = thumbBlobKey
            imgReturn['thumbUrl'] = thumbUrl

        imgReturn['actionMsg'] = 'Completed'


    except Exception, error:
        imgReturn['actionMsg'] = error

    return imgReturn


""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist/videowork(.*)', VideoWorkHandler),
                                      ('/artist/videoaddredirect(.*)', VideoAddRedirect),
                                      ('/artist/videoredirect(.*)', VideoWorkRedirect)],
                                     debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
