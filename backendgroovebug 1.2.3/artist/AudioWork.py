""" This Handler is responsible for making the API calls to youtube, parsing the
    json data for a given artist, creating a formatted HTML document with youtube
    video links, and returning it when queried using our internal API
    the wrapper for videos will be
    http://backendgroovebug.appspot.com/v1/videos?artist="""


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
import echonestlib as echonest
import urllib2, urllib, re

if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']


""" This method removes HTML or XML character references and entities from a text
    string, and returns the plain text, as a Unicode string, if necessary.
    got from:  http://effbot.org/zone/re-sub.htm#unescape-html"""
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
""" --- """

""" This function recieves an artist name as an input and outputs an array of dictionaries
    which contain a title, video link, and thumbnail link. There is an optional second
    argument for the max amount of entries in the array, default is 20."""
def GetArtistAudio(artist, maxResults = 20):
## Encode results into unicode which can be parsed by iTunes API
    artist = artist.encode('utf-8')
    artistName = urllib.quote_plus(artist)
## Initialize list that will contain dictionary entries with video data
    audio = []
    
## Populate videos list with dictionary entries with "title", "thumbnail", and video link data
    audioRec = db.GqlQuery("SELECT * FROM PromotedAudio WHERE artistName = :1 LIMIT 20",
                           artistName).fetch(20)
    if len(audioRec) > 0:
        audio = audioRec
        if audio:
            if not len(audio) > 0:
                audio = []
                    

## Return populated audio list
    return audio
""" --- """



""" Class that handles video requests"""
class AudioWorkHandler(webapp.RequestHandler):
    def get(self, artist):
## Use GetArtistVideos method to obtain video data from youtube
        artist = self.request.get("artist")
        artistEnc = artist.encode('utf-8')
        artistEnc = urllib.quote_plus(artistEnc)
        actionMsg = self.request.get("actionMsg")
        if not actionMsg:
            actionMsg = ''
        audio = GetArtistAudio(artist)

        upload_url = blobstore.create_upload_url('/artist/audioredirect')
# If there are no audio for the artist, display error message
        if not audio:
            if actionMsg == '':
                actionMsg = 'Sorry, there is no audio found for ' + artist
            context = {'error' : actionMsg, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'audiowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# Otherwise, use audio data to create html document
        else:
            if actionMsg != '':
                context = {'error' : actionMsg, 'audio' : audio, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            else:
                context = {'audio' : audio, 'artist' : artist, 'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'audiowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
""" --- """


""" Class that handles video requests"""
class AudioWorkRedirect(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, artist):
        artist = self.request.get('artist')
        artistEnc = self.request.get('artistEnc')
        actionMsg = ''

        if self.request.get('addTrack'):
            if artistEnc != '':
                if self.request.get('audiofile'):
                    trkToAdd = self.request.get('audiofile')
                    trkTitle = self.request.get('songtitle')
                    if not trkTitle:
                        actionMsg = 'You have not selected a title for the audio file'
                    else:
                        if trkTitle == '':
                            actionMsg = 'You have not selected a title for the audio file'

                    if actionMsg == '':
                        trkImg = self.request.get('imgfile')
                        if not trkImg:
                            actionMsg = 'You have not selected an image for the audio file'
                        
                    if actionMsg == '':
                        try:
                            upload_files = self.get_uploads('audiofile')  # 'file' is file upload field in the form
                            blob_info = upload_files[0]
                            trkBlobKey = blob_info.key()
                            uploadimg_files = self.get_uploads('imgfile')
                            blob_info2 = uploadimg_files[0]
                            imgBlobKey = blob_info2.key()
                            if trkBlobKey and imgBlobKey:
                                audioRec = models.PromotedAudio(artistName = artistEnc, title = trkTitle)

                                trkBlobUrl = 'http://' + str(hostUrl) + '/artist/audioserve?resource=' + str(trkBlobKey)
                                imgJson = getDrawerImageInfo(imgBlobKey)
                                imgUrl = imgJson['imgUrl']
                                thumbUrl = imgJson['thumbUrl']
                                thumbBlobKey = imgJson['thumbBlobKey']
                                trkMagUrl = 'http://' + str(hostUrl) + '/v1/magazine?artist=' + artistEnc

                                #audioRec.title = trkTitle
                                audioRec.blobKey = str(trkBlobKey)
                                audioRec.url = trkBlobUrl
                                audioRec.imgBlobkey = str(imgBlobKey)
                                audioRec.imgUrl = imgUrl
                                audioRec.thumbBlobkey = str(thumbBlobKey)
                                audioRec.thumbUrl = thumbUrl
                                audioRec.put()
                                actionMsg = 'Audio and Image Added!!!'
                                #self.redirect('/artist/audiowork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
                            else:
                                actionMsg = 'Blob write did not work (unknown error)'
                        except Exception, error:
                            actionMsg = error
                            self.response.out.write(actionMsg)
                            return 'ok'
                else:
                    actionMsg = 'You have not selected an audio file'

            else:
                actionMsg = 'There is no artist name'
                artistName = ''
        elif self.request.get('deleteTrack'):
            delBlobKey = self.request.get('deleteTrack')
            delImgBlobKey = self.request.get('deleteImgFull')
            delThmbBlobKey = self.request.get('deleteImg')
            
            if delBlobKey != '':
                if delImgBlobKey:
                    actionMsg = delAudioFile(artistEnc, delBlobKey, delImgBlobKey, delThmbBlobKey)
                else:
                    actionMsg = delAudioFile(artistEnc, delBlobKey)
            else:
                if delImgBlobKey:
                    delBlobKey = None
                    actionMsg = delAudioFile(artistEnc, delBlobKey, delImgBlobKey, delThmbBlobKey)
        else:
            actionMsg = 'No action requested'

## Use GetArtistVideos method to obtain video data from youtube
        audio = GetArtistAudio(urllib.unquote_plus(artistEnc))
        upload_url = blobstore.create_upload_url('/artist/audioredirect')
        if actionMsg != '':
            try:
                self.redirect('/artist/audiowork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
            except Exception, error:
                self.response.out.write(actionMsg)
                #self.response.out.write(error)
                return 'ok'

# If there are no videos found on youtube for the artist, display error message
        elif not audio:
            context = {'error' : 'Sorry, there is no audio found for ' + urllib.unquote_plus(artistEnc), 'artist' : urllib.unquote_plus(artistEnc),
                       'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'audiowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
            
# Otherwise, use audio data to create html document
        else:
            context = {'audio' : audio, 'artist' : urllib.unquote_plus(artistEnc), 'artistEnc' : artistEnc, 'upload' : upload_url}
            tmpl = path.join(path.dirname(__file__), 'audiowork.html')
            html = render(tmpl, context)
            self.response.out.write(html)

""" --- """

def delAudioFile(artistEnc, blobKey, imgBlobKey=None, thmbBlobKey=None):
    actionMsg = ''
    AudioDeleted = False
    ImageDeleted = False
    ThumbDeleted = False
    try:
        audioRec = db.GqlQuery("SELECT * FROM PromotedAudio WHERE blobKey = :1 LIMIT 1",
                           blobKey).fetch(1)
        
        if len(audioRec) > 0:
            
            drawerRecs = db.GqlQuery("SELECT * FROM ArtistDrawer WHERE audioToPromote = :1 LIMIT 100", blobKey).fetch(100)

            if len(drawerRecs) > 0:
                for entry in drawerRecs:
                    entry.delete()

            if thmbBlobKey:
                delFile = blobstore.BlobInfo.get(thmbBlobKey)
                if delFile:
                    delFile.delete()
                    audioRec[0].thumbBlobkey = None
                    audioRec[0].thumbUrl = None
                    audioRec[0].put()
                    ThumbDeleted = True
                else:
                    actionMsg = 'Thumbnail Blob not found'
            else:
                ThumbDeleted = True
                    
            if imgBlobKey:
                delFile = blobstore.BlobInfo.get(imgBlobKey)
                if delFile:
                    delFile.delete()
                    audioRec[0].imgBlobkey = None
                    audioRec[0].imgUrl = None
                    audioRec[0].put()
                    ImageDeleted = True
                else:
                    actionMsg = 'Image Blob not found'
            else:
                ImageDeleted = True

            delFile = blobstore.BlobInfo.get(blobKey)
            if delFile:
                delFile.delete()
                AudioDeleted = True
            else:
                actionMsg = 'Audio Blob not found'
        

            if AudioDeleted and ImageDeleted and ThumbDeleted:
                for drawerRec in audioRec[0].promoted_to_artists:
                    drawerRec.delete()
                        
                audioRec[0].delete()
                actionMsg = 'Track Deleted'
            else:
                if not AudioDeleted:
                    actionMsg = 'Audio not Deleted'
                elif not ImageDeleted:
                    actionMsg = 'Image not Deleted'
                elif not ThumbDeleted:
                    actionMsg = 'Thumbnail not Deleted'
                                     
        else:
            actionMsg = 'Audio record not found for ' + urllib.unquote(artistEnc)
                    
    except Exception, error:
        actionMsg = error

    return actionMsg

def getDrawerImageInfo(imgBlobKey):
    imgReturn = {}
    minWidth = 300
    minHeight = 300
    maxImpWidth = 1200
    maxImpHeight = 1200
    maxWidth = 800
    maxHeight = 600
    actionMsg = ''
    
    try:
        blob_reader = blobstore.BlobReader(imgBlobKey)
        trkImg = blob_reader.read()
        imgW = images.Image(trkImg).width
        imgH = images.Image(trkImg).height
        scaleW = imgW
        scaleH = imgH
             
        imgUrl = images.get_serving_url(imgBlobKey)
        imgReturn['imgBlobKey'] = imgBlobKey
        imgReturn['imgUrl'] = imgUrl

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


""" Class that handles form data submission"""
class RedirectDrawerHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        if self.request.get('back'):
            artistEnc = self.request.get('back')
            self.redirect('/artist/audiowork?artist=' + artistEnc)
            
    def post(self):
        user = users.get_current_user()
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/audiowork')

        artist = self.request.get('artist')
        artistEnc = self.request.get('artistEnc')
        itemKey = self.request.get('itemKey')

        actionMsg = ''

        if artistEnc != '':
            if self.request.get('changeAudio'):
                if self.request.get('audiofile'):
                    origBlobKey = self.request.get('changeAudio')
                    trkToAdd = self.request.get('audiofile')
                    trkTitle = self.request.get('songtitle')
                    if not trkTitle:
                        actionMsg = 'You have not selected a title for the audio file'
                    else:
                        if trkTitle == '':
                            actionMsg = 'You have not selected a title for the audio file'
                        
                    if actionMsg == '':
                        try:
                            upload_files = self.get_uploads('audiofile')  # 'file' is file upload field in the form
                            blob_info = upload_files[0]
                            trkBlobKey = blob_info.key()

                            if trkBlobKey:
                                promoRec = db.get(itemKey)
                                if promoRec:
                                    trkBlobUrl = 'http://' + str(hostUrl) + '/artist/audioserve?resource=' + str(trkBlobKey)
                                    promoRec.blobKey = str(trkBlobKey)
                                    promoRec.url = trkBlobUrl

                                    if origBlobKey:
                                        delFile = blobstore.BlobInfo.get(origBlobKey)
                                        if delFile:
                                            delFile.delete()
                                        else:
                                            actionMsg = 'Audio Blob not found'
                                            
                                    if actionMsg == '':        
                                        promoRec.put()
                                        actionMsg = 'Audio Updated!!!'
                                        
                                        self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))
                                else:
                                    actionMsg = 'Audio file was not created'
                            else:
                                actionMsg = 'Blob write did not work (unknown error)'
                        except Exception, error:
                            actionMsg = error

                else:
                    actionMsg = 'You have not selected an audio file'

                self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg)) 
            elif self.request.get('changeImage'):
                if self.request.get('imgfile'):
                    origBlobKey = self.request.get('changeImage')
                    trkTitle = self.request.get('songtitle')
                    if not trkTitle:
                        actionMsg = 'You have not selected a title for the audio file'
                    else:
                        if trkTitle == '':
                            actionMsg = 'You have not selected a title for the audio file'
                        
                    if actionMsg == '':
                        try:
                            upload_files = self.get_uploads('imgfile')  # 'file' is file upload field in the form
                            blob_info = upload_files[0]
                            imgBlobKey = blob_info.key()
                            
                            if imgBlobKey:
                                promoRec = db.get(itemKey)
                                if promoRec:
                                    origThmbBlobKey = promoRec.thumbBlobkey
                                    origItemBlobKey = promoRec.blobKey
                                    imgJson = getDrawerImageInfo(imgBlobKey)
                                    imgUrl = imgJson['imgUrl']
                                    thumbUrl = imgJson['thumbUrl']
                                    thumbBlobKey = imgJson['thumbBlobKey']
         
                                    promoRec.imgBlobkey = str(imgBlobKey)
                                    promoRec.imgUrl = imgUrl
                                    promoRec.thumbBlobkey = str(thumbBlobKey)
                                    promoRec.thumbUrl = thumbUrl

                                    if origBlobKey:
                                        delFile = blobstore.BlobInfo.get(origBlobKey)
                                        if delFile:
                                            delFile.delete()
                                        else:
                                            actionMsg = 'Image Blob not found'

                                    if origThmbBlobKey:
                                        delFile = blobstore.BlobInfo.get(origThmbBlobKey)
                                        if delFile:
                                            delFile.delete()
                                        else:
                                            actionMsg = 'Thumbnail Blob not found'

                                    if actionMsg == '':
                                        audioRec.put()
                                        actionMsg = 'Image Updated!!!'
                                        #self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))
                                else:
                                    actionMsg = 'PromotedAudio record not found'
                            else:
                                actionMsg = 'Blob write did not work (unknown error)'
                        except Exception, error:
                            actionMsg = error
                else:
                    actionMsg = 'You have not selected an image file'
                self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg)) 
            elif self.request.get('changeTitle'):
                if self.request.get('songtitle'):
                    origBlobKey = self.request.get('changeTitle')
                    trkTitle = self.request.get('songtitle')
                    if not trkTitle:
                        actionMsg = 'You have not selected a title for the audio file'
                    else:
                        trkTitle = trkTitle.strip()
                        if trkTitle == '':
                            actionMsg = 'The title for the audio file is blank'
                        else:
                            try:
                                origRec = db.get(itemKey)
                                if origRec:
                                    if origRec.title != trkTitle:
                                        origRec.title = trkTitle
                                        
                                        for drawerRec in origRec.promoted_to_artists:
                                            drawerRec.promotedTitle = trkTitle
                                            drawerRec.put()

                                        origRec.put()
                                    
                                        actionMsg = 'Track Renamed!!!'
                                    else:
                                        actionMsg = 'The New Title Is The Same'    
                                else:
                                    actionMsg = 'Original record not found'
                                    
                            except Exception, error:
                                actionMsg = error
                                self.response.out.write(actionMsg)
                                return 'ok'
                            
                self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))
                
            elif self.request.get('verify'):
                if self.request.get('artistList'):
                    drawerItemKey = self.request.get('verify')
                    artistText = self.request.get('artistList').strip()
                    currDrawerItem = db.get(itemKey)
                    if not currDrawerItem:
                        actionMsg = 'Promoted Audio record not found'
                        self.response.out.write(actionMsg)    
                    else:                    
                        artistText = unescape(artistText)
                        artistList = re.findall('[^\n|\r]+', artistText)

                        
                        correctedArtists = []
                        errorArtists = []
                        currDrawerItem.PromotedToList = []
                        currDrawerItem.artistListErrors = []

                        correctedArtistList = echonest.CorrectArtistNames(artistList)

                        for i, artist in enumerate(artistList):
                            artist = artist.encode('utf-8')
                            if correctedArtistList[i] is None:
                                errorArtists.append(artist)
                                currDrawerItem.artistListErrors.append(artist)
                            else:
                                correctedArtist = correctedArtistList[i]
                                currDrawerItem.PromotedToList.append(correctedArtist)
                                correctedArtist = correctedArtist.encode('utf-8')
                                correctedArtists.append(correctedArtist)
                                     
                        correctedString = ""
                        if self.request.get('artistListErrors'):
                            errorString = self.request.get('artistListErrors')
                            errorString = unescape(errorString)
                            errorString = errorString.encode('utf-8')
                        else:
                            errorString = ""
                            
                        if not errorArtists == []:
                            for artist in errorArtists:
                                errorString = errorString + artist + "\n"
                        if not correctedArtists == []:
                            for artist in correctedArtists:
                                    correctedString = correctedString + artist + "\n"

                        currDrawerItem.put()

                        actionMsg = 'Verify Results'

                        self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))   

                else:
                    actionMsg = 'Artist list is empty'
                    self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))     
            elif self.request.get('submit'):
                drawerItemKey = self.request.get('submit')
                trkTitle = self.request.get('songtitle')
                actionMsg = ''
                if self.request.get('artistList'):
                    artistText = self.request.get('artistList').strip()
                else:
                    artistText = ''

                artistText = unescape(artistText)
                artistList = re.findall('[^\n|\r]+', artistText)
                artistListEnc = []

                promoRec = db.get(itemKey)

                if promoRec:
                    promoRec.PromotedToList = []

                    drawerList = []
                    for drawerRec in promoRec.promoted_to_artists:
                        drawerList.append(drawerRec.artistName)

                    for drawerArtist in artistList:
                        promoRec.PromotedToList.append(drawerArtist)
                        drawerArtist = drawerArtist.encode('utf-8')
                        drawerArtistEnc = urllib.quote_plus(drawerArtist)
                        artistListEnc.append(drawerArtistEnc)

                        if drawerArtistEnc not in drawerList:
                            drawerRec = models.ArtistDrawer(artistName = drawerArtistEnc)
                            drawerRec.promotedArtist = artistEnc
                            drawerRec.promotedTitle = trkTitle
                            drawerRec.audioToPromote = promoRec
                            drawerRec.put()
                    
                    for drawerRec in promoRec.promoted_to_artists:
                        if drawerRec.artistName not in artistListEnc:
                            drawerRec.delete()

                    promoRec.put()
                    actionMsg = 'Drawer Records Updated'
                else:
                    actionMsg = 'PromotedAudio Record Not Found'
                    
                self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))   

            else:
                actionMsg = 'It did not recognize the changeaudio or changeimage'
                self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg)) 
        else:
            actionMsg = 'it did not recognize the artist name'
            self.redirect('/artist/editdrawer?editKey=' + str(itemKey) + '&actionMsg=' + urllib.quote(actionMsg))    


""" Class that handles composite editor page"""
class EditDrawerHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/audiowork')
        
        drawerItemKey = self.request.get('editKey')
        
        actionMsg = self.request.get('actionMsg')
        if not actionMsg:
            actionMsg = ''

        #currDrawerItem = db.GqlQuery("SELECT * FROM PromotedAudio WHERE blobKey = :1 LIMIT 1", drawerItemKey).fetch(1)
        currDrawerItem = db.get(drawerItemKey)
        
        if not currDrawerItem:
            self.response.out.write('Promoted Audio File Not Found In Get')
            return 'ok'
        else:
            drawerPage = {}
            drawerPage['drawerItemKey'] = drawerItemKey

            drawerPage['artist'] = urllib.unquote_plus(currDrawerItem.artistName.encode('utf-8'))
            drawerPage['artistEnc'] = currDrawerItem.artistName

            if currDrawerItem.PromotedToList:
                artistList = currDrawerItem.PromotedToList
            else:
                artistList = []
            artistListString = ''
            for artist in artistList:
                artistListString = artistListString + artist + '\n'
            drawerPage['artistList'] = artistListString

            if currDrawerItem.artistListErrors:
                artistListErrors = currDrawerItem.artistListErrors
            else:
                artistListErrors = []
            artistListErrorsString = ''
            for artist in artistListErrors:
                artistListErrorsString = artistListErrorsString + artist + '\n'
            drawerPage['artistListErrors'] = artistListErrorsString

            similarBase = 'http://developer.echonest.com/api/v4/artist/similar?'
            apiKey = 'api_key=269A92REW5YH3KNZW&'
            similarArgs = { 'format' : 'json',
                           'results' : '100',}
            similarUrl = str(similarBase) + str(apiKey) + str(urllib.urlencode(similarArgs)) + '&name=' + currDrawerItem.artistName
            similarJson = models.RetryLoadJson(similarUrl)
            similarListString = ''
            if similarJson['response']['status']['code'] > 0:
                actionMsg = 'Similar artists not found'
            else:    
                for artist in similarJson['response']['artists']:
                    simArtist = artist['name']
                    similarListString = similarListString + simArtist + '\n'
           
            drawerPage['similarList'] = similarListString
            
            drawerPage['title'] = currDrawerItem.title
            drawerPage['url'] = currDrawerItem.url
            drawerPage['blobKey'] = currDrawerItem.blobKey
            drawerPage['imgUrl'] = currDrawerItem.imgUrl
            drawerPage['imgBlobKey'] = currDrawerItem.imgBlobkey
            drawerPage['thumbUrl'] = currDrawerItem.thumbUrl
            drawerPage['thumbBlobKey'] = currDrawerItem.thumbBlobkey
            pagekey = currDrawerItem.key()

            upload_url = blobstore.create_upload_url('/artist/redirectdrawer')
            if actionMsg == '':
                actionMsg = 'Edit Promote To List Page'
            context = {'title' : actionMsg,
                       'user' : userName,
                       'logoutUrl' : logoutUrl,
                       'upload' : upload_url,
                       'drawerPage' : drawerPage,}
            tmpl = path.join(path.dirname(__file__), 'drawerManager.html')
            html = render(tmpl, context)
            self.response.out.write(html)

    def post(self):
        user = users.get_current_user()
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/audiowork')
        
        drawerItemKey = self.request.get('editKey')
        actionMsg = self.request.get('actionMsg')
        
        if not actionMsg:
            actionMsg = ''


        artistList = []
        artistListErrors = []
            
        #currDrawerItem = db.GqlQuery("SELECT * FROM PromotedAudio WHERE blobKey = :1 LIMIT 1", drawerItemKey).fetch(1)
        currDrawerItem = db.get(drawerItemKey)
        
        if not currDrawerItem:
            self.response.out.write('Promoted Audio File Not Found In Post')
            return 'ok'
        else:
            drawerPage = {}
            drawerPage['drawerItemKey'] = drawerItemKey

            drawerPage['artist'] = urllib.unquote_plus(currDrawerItem.artistName.encode('utf-8'))
            drawerPage['artistEnc'] = currDrawerItem.artistName

            if artistList == []:
                artistList = currDrawerItem.PromotedToList
            artistListString = ''
            for artist in artistList:
                artistListString = artistListString + artist + '\n'
            drawerPage['artistList'] = artistListString

            if artistListErrors == []:
                artistList = currDrawerItem.artistListErrors

            artistListErrorsString = ''
            for artist in artistListErrors:
                artistListErrorsString = artistListErrorsString + artist + '\n'
            drawerPage['artistListErrors'] = artistListErrorsString

            similarBase = 'http://developer.echonest.com/api/v4/artist/similar?'
            apiKey = 'api_key=269A92REW5YH3KNZW&'
            similarArgs = { 'format' : 'json',
                           'results' : '100',}
            similarUrl = str(similarBase) + str(apiKey) + str(urllib.urlencode(similarArgs)) + '&name=' + currDrawerItem.artistName
            similarJson = models.RetryLoadJson(similarUrl)
            similarListString = ''
            if similarJson['response']['status']['code'] > 0:
                actionMsg = 'Similar artists not found'
            else:    
                for artist in similarJson['response']['artists']:
                    simArtist = artist['name']
                    similarListString = similarListString + simArtist + '\n'
           
            drawerPage['similarList'] = similarListString
            
            drawerPage['title'] = currDrawerItem.title
            drawerPage['url'] = currDrawerItem.url
            drawerPage['blobKey'] = currDrawerItem.blobKey
            drawerPage['imgUrl'] = currDrawerItem.imgUrl
            drawerPage['imgBlobKey'] = currDrawerItem.imgBlobkey
            drawerPage['thumbUrl'] = currDrawerItem.thumbUrl
            drawerPage['thumbBlobKey'] = currDrawerItem.thumbBlobkey
            pagekey = currDrawerItem.key()

            upload_url = blobstore.create_upload_url('/artist/redirectdrawer')
            if actionMsg == '':
                actionMsg = 'Edit Promote To List Page'
            context = {'title' : actionMsg,
                       'user' : userName,
                       'logoutUrl' : logoutUrl,
                       'upload' : upload_url,
                       'drawerPage' : drawerPage,}
            tmpl = path.join(path.dirname(__file__), 'drawerManager.html')
            html = render(tmpl, context)
            self.response.out.write(html)
""" --- """


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('audiofile')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/artist/audioserve/%s' % blob_info.key())

class AudioServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = self.request.get('resource')
        resource = str(urllib.unquote(resource))
        
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(resource)



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist/audiowork(.*)', AudioWorkHandler),
                                      ('/artist/audioredirect(.*)', AudioWorkRedirect),
                                      ('/artist/audioserve([^/]+)?', AudioServeHandler),
                                      ('/artist/redirectdrawer', RedirectDrawerHandler),
                                      ('/artist/editdrawer', EditDrawerHandler)],
                                     debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
