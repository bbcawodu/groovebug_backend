""" This Handler is responsible for making the API calls to echonest, parsing the
    json data for a given artist, creating our own json formatted dictionary of
    artist background images, and returning it when queried using our internal API
    the wrapper for similar artists will be
    http://backendgroovebug.appspot.com/v1/background?artist="""


from __future__ import with_statement
import os
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import urllib2, urllib, datetime
from datetime import tzinfo, timedelta, datetime
import DataModels as models
from google.appengine.api import images
from google.appengine.api import urlfetch, apiproxy_stub_map, memcache
from google.appengine.api import files
import random


if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']

defBackImages = ['concert-generic.png', 'concert-generic2.png', 'concert-generic3.png']

MAX_SIMULTANEOUS_ASYNC_URLFETCH_REQUESTS = 10
MAX_PICS = 10
MIN_PICS = 3

rpcUrlArr = {}


class AsyncURLFetchManager(object):

    def __init__(self):
        self.active_fetches = []
        self.pending_fetches = []
        self.artistImgCnt = 0

    def set_image_cnt(self, imgCnt):
        self.artistImgCnt = imgCnt

    def handle_result(self, rpc):

        imgCnt = self.artistImgCnt
        try:
            result = rpc.get_result()
            if result.status_code == 200:
                if self.artistImgCnt < MAX_PICS:
                    artist = rpcUrlArr[rpc]['artist']
                    imgUrl = rpcUrlArr[rpc]['url']
                    imgLic = rpcUrlArr[rpc]['license']
                    imgUrlRslt = writeToBlob(artist, imgUrl, imgLic, result.content, rpc, imgCnt)
                    if imgUrlRslt['imgUrl'] != '':
                        self.artistImgCnt += 1
        except Exception, error:
            #print error
            imgUrlRslt = {'imgUrl': '', 'reducedUrl' : '', 'license' : {}, 'thumbUrl' : ''}

    def fetch_asynchronously(self, url, deadline=10,
                             callback=handle_result, cb_args=[], cb_kwargs={},
                             **kwargs):

        """
        Asynchronously fetches the requested url.  Ensures that the maximum
        number of simultaneous asynchronous fetches is not exceeded.

        url      - the url to fetch
        deadline - maximum number of seconds to wait for a response
        callback - if given, called upon completion.  The first argument will be
                   the rpc object (which contains the response).  If cb_args
                   or cb_kwargs were provided then these will be passed to
                   callback as additional positional and keyword arguments.

        All other keyword arguments are passed to urlfetch.make_fetch_call().

        Returns the RPC which will be used to fetch the URL.
        """
        rpc = urlfetch.create_rpc(deadline=deadline)
        rpc.callback = lambda : self.__fetch_completed(rpc, callback)

        f = lambda : urlfetch.make_fetch_call(rpc, url, **kwargs)
        if self.artistImgCnt < MAX_PICS:
            if len(self.active_fetches) < MAX_SIMULTANEOUS_ASYNC_URLFETCH_REQUESTS:
                self.__fetch(rpc, f)
            else:
                self.pending_fetches.append( (rpc,f) )
        return rpc

    def __fetch(self, rpc, f):
        self.active_fetches.append(rpc)
        f()

    def __fetch_completed(self, rpc, callback):
        self.active_fetches.remove(rpc)
        if self.artistImgCnt < MAX_PICS:
            if self.pending_fetches:
                # we just finished a fetch, so start the next one
                self.__fetch(*self.pending_fetches.pop(0))    
            if callback:
                result = self.handle_result(rpc)

    def wait(self):
        """Blocks until all asynchronous fetches have been completed."""
        while self.active_fetches:
            # Wait until this RPC finishes.  This will automatically call our
            # callback, which will start the next pending fetch (if any) and
            # remove the finished RPC from active_fetches.
            # This is *sub-optimal* - it would be better if we could poll the
            # RPCS and do a non-blocking check to see if they were ready.  By
            # arbitrarily waiting on the first RPC, we may miss out on another
            # RPC which may finish sooner.
            self.active_fetches[0].wait()


""" --- """

            

""" Section ending with "---" defines code that handles exceptions when making urllib2.urlopen requests"""
def RetryLoadJson(url, counter = 0, maxTries = 3):
    try:
        loadedJson = json.load(urllib2.urlopen(url))
    except Exception:
        if counter < maxTries:
            counter += 1
            return RetryLoadJson(url, counter)
        else:
            return []
    return loadedJson

""" --- """


""" This section of code which ends with a "---" block defines the method that recieves
    an artist name as an input and outputs a json formatted dictionary of artist background
    images"""
def GetArtistBackground(artistName, minPics = MIN_PICS, maxPics = MAX_PICS):
# Encode results into unicode which can be parsed by Echonest API
    artistName = artistName.encode('utf-8')
    artistName = urllib.quote_plus(artistName)

# Initiallize the dictionary that will eventually be converted to json
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0'}
    finalPreJson['images'] = []
    cachedImgs = []
    currUrlList = []
    cachedUrlList = []
    if artistName:
        #artist7DayImgCnt = chk7DayImgCnt(artistName)
        #return artist7DayImgCnt
        cachedImgs = getManuallyStored(artistName)
        cachedUrlList = []
        for cEntry in cachedImgs:
            if cEntry['url']:
                cachedUrlList.append(cEntry['url'])
        cachedUrlSet = set(cachedUrlList)
            
        data = memcache.get('artistImages' + artistName)
        if data is not None:
            if data != []:
                if len(data) > minPics:
                    finalPreJson['images'] = data
                    finalJson = json.dumps(finalPreJson)
                    return finalJson
                else:
                    for entry in data:
                        if entry.has_key('license'):
                            if entry['license'].has_key('type'):
                                if entry['license']['type']:
                                    if entry['license']['type'] == 'Manually Replaced' or entry['license']['type'] == 'Manually Added':
                                        if entry['url'] not in cachedUrlSet:
                                            cachedUrlList.append(entry)
  
            
        if len(cachedUrlList) < minPics:
        # Perform lookup of background images for given artist
            backgroundBase = 'http://developer.echonest.com/api/v4/artist/images?'
            apiKey = 'api_key=269A92REW5YH3KNZW&'
            backgroundArgs = { 'format' : 'json',
                           'results' : '100',}
            backgroundUrl = str(backgroundBase) + str(apiKey) + str(urllib.urlencode(backgroundArgs)) + '&name=' + artistName
            backgroundJson = RetryLoadJson(backgroundUrl)
            if backgroundJson == []:
                finalPreJson['status']['error'] = 'echonest API request timed out'
                finalPreJson['images'] = cachedImgs
                finalJson = json.dumps(finalPreJson, separators=(',',':'))
                return finalJson

        # Return blank arrays for everything if artist isnt found
            #for testing - return backgroundJson
            if backgroundJson['response']['status']['code'] > 0:
                finalPreJson['status']['error'] = 'artists not found'

                r = random.randint(0, (len(defBackImages) - 1))
                defBack = defBackImages[r]
                backUrlAdd = {'url' : 'http://' + str(hostUrl) + '/htmlimages/backgrounds/' + str(defBack),
                              'reduced' : 'http://' + str(hostUrl) + '/htmlimages/backgrounds/' + str(defBack),
                              'license' : {'thumbnail' : 'http://' + str(hostUrl) + '/htmlimages/missing_profile_icon.png'}}
                finalPreJson['images'].append(backUrlAdd)
                    
                finalJson = json.dumps(finalPreJson, separators=(',',':'))
                return finalJson

        # Insert images into dictionary set to be returned
            finalPreJson['images'] = backgroundJson['response']['images']
        else:
            finalPreJson['images'] = []
    else:
        r = random.randint(0, (len(defBackImages) - 1))
        defBack = defBackImages[r]
        backUrlAdd = {'url' : 'http://' + str(hostUrl) + '/htmlimages/backgrounds/' + str(defBack),
                      'reduced' : 'http://' + str(hostUrl) + '/htmlimages/backgrounds/' + str(defBack),
                      'license' : {'thumbnail' : 'http://' + str(hostUrl) + '/htmlimages/missing_profile_icon.png'}}
        finalPreJson['images'].append(backUrlAdd)
            
        finalJson = json.dumps(finalPreJson, separators=(',',':'))
        return finalJson
        
    currUrlList = cachedUrlList
    loopEnd = len(finalPreJson['images'])
    artistImgCnt = chkImgCnt(artistName)
    
    if artistImgCnt < minPics:
        rpcs = []
        currCallList = []
        uCalls = AsyncURLFetchManager()
        uCalls.set_image_cnt(artistImgCnt)
        for i, entry in enumerate(finalPreJson['images']):
            imgUrl = finalPreJson['images'][i]['url']
            imgUrl = imgUrl.strip().lower()
            if imgUrl not in currCallList:
                currCallList.append(imgUrl)
                imgChkExists = chkExistsLic(finalPreJson['images'][i])
                if imgChkExists['imgUrl'] == '':
                    rpc = uCalls.fetch_asynchronously(finalPreJson['images'][i]['url'])
                    rpcUrlArr[rpc] = {'url' : finalPreJson['images'][i]['url'],
                                      'license' : finalPreJson['images'][i]['license'],
                                      'artist' : artistName, 'imgUrl' : '', 'reducedUrl' : '', 'thumbUrl' : ''}
                    rpcs.append(rpc)
                else:
                    finalPreJson['images'][i]['url'] = imgChkExists['imgUrl']
                    if imgChkExists['license']:
                        finalPreJson['images'][i]['license'] = imgChkExists['license']
                    else:
                        finalPreJson['images'][i]['license'] = {}
                    finalPreJson['images'][i]['license']['thumbnail'] = imgChkExists['thumbUrl']
                    finalPreJson['images'][i]['reduced'] = imgChkExists['reducedUrl']
            else:
                finalPreJson['images'][i]['url'] = ''

        uCalls.wait()
        for rpc in rpcs:       

            for k, entry in enumerate(finalPreJson['images']):
                if finalPreJson['images'][k]['url'] == rpcUrlArr[rpc]['url']:
                    if rpcUrlArr[rpc]['imgUrl'] == '':
                        finalPreJson['images'][k]['url'] = ''
                        finalPreJson['images'][k]['license'] = {}
                        finalPreJson['images'][k]['license']['thumbnail'] = ''
                        finalPreJson['images'][k]['reduced'] = ''
                    else:
                        finalPreJson['images'][k]['url'] = rpcUrlArr[rpc]['imgUrl']
                        finalPreJson['images'][k]['license'] = rpcUrlArr[rpc]['license']
                        finalPreJson['images'][k]['license']['thumbnail'] = rpcUrlArr[rpc]['thumbUrl']
                        if rpcUrlArr[rpc]['reducedUrl']:
                            finalPreJson['images'][k]['reduced'] = rpcUrlArr[rpc]['reducedUrl']
                        else:
                            finalPreJson['images'][k]['reduced'] = rpcUrlArr[rpc]['imgUrl']
            
        for l, entry in enumerate(finalPreJson['images']):
            if entry['url'] != {}:
                chkRslt = chkDBExists(entry['url'])
                if chkRslt != {}:
                    if chkRslt['imgUrl'] not in currUrlList:
                        currUrlList.append(chkRslt['imgUrl'])
                        finalPreJson['images'][l]['url'] = chkRslt['imgUrl']
                        if chkRslt['license']:
                            finalPreJson['images'][l]['license'] = chkRslt['license']
                        else:
                            finalPreJson['images'][l]['license'] = {}

                        finalPreJson['images'][l]['license']['thumbnail'] = chkRslt['thumbUrl']
                        if chkRslt['reducedUrl']:
                            finalPreJson['images'][l]['reduced'] = chkRslt['reducedUrl']
                        else:
                            finalPreJson['images'][l]['reduced'] = chkRslt['imgUrl']
                    else:
                        finalPreJson['images'][l]['url'] = ''
                        finalPreJson['images'][l]['license'] = {}
                        finalPreJson['images'][l]['license']['thumbnail'] = ''
                        finalPreJson['images'][l]['reduced'] = ''
                else:
                    finalPreJson['images'][l]['url'] = ''
                    finalPreJson['images'][l]['license'] = {}
                    finalPreJson['images'][l]['license']['thumbnail'] = ''
                    finalPreJson['images'][l]['reduced'] = ''
    else:
        for i, entry in enumerate(finalPreJson['images']):
            if entry['url'] != {}:
                chkRslt = chkExistsLic(entry)
                if chkRslt['imgUrl'] != '':
                    if chkRslt['imgUrl'] not in currUrlList:
                        currUrlList.append(chkRslt['imgUrl'])
                        finalPreJson['images'][i]['url'] = chkRslt['imgUrl']
                        if chkRslt['license']:
                            finalPreJson['images'][i]['license'] = chkRslt['license']
                        else:
                            finalPreJson['images'][i]['license'] = {}

                        finalPreJson['images'][i]['license']['thumbnail'] = chkRslt['thumbUrl']
                        if chkRslt['reducedUrl']:
                            finalPreJson['images'][i]['reduced'] = chkRslt['reducedUrl']
                        else:
                            finalPreJson['images'][i]['reduced'] = chkRslt['imgUrl']
                    else:
                        finalPreJson['images'][i]['url'] = ''
                        finalPreJson['images'][i]['license'] = {}
                        finalPreJson['images'][i]['license']['thumbnail'] = ''
                        finalPreJson['images'][i]['reduced'] = ''
                else:
                    finalPreJson['images'][i]['url'] = ''
                    finalPreJson['images'][i]['license'] = {}
                    finalPreJson['images'][i]['license']['thumbnail'] = ''
                    finalPreJson['images'][i]['reduced'] = ''
        
    for i in reversed(range(0, len(finalPreJson['images']))):
        if finalPreJson['images'][i]['url'] == '':
            del finalPreJson['images'][i]

    if len(cachedImgs) == 0:
        if len(finalPreJson['images']) == 0:
            r = random.randint(0, (len(defBackImages) - 1))
            defBack = defBackImages[r]
            backUrlAdd = {'url' : 'http://' + str(hostUrl) + '/htmlimages/backgrounds/' + str(defBack),
                          'reduced' : 'http://' + str(hostUrl) + '/htmlimages/backgrounds/' + str(defBack),
                          'license' : {'thumbnail' : 'http://' + str(hostUrl) + '/htmlimages/missing_profile_icon.png'}}
            finalPreJson['images'].append(backUrlAdd)
    else:
        if len(finalPreJson['images']) == 0:
            finalPreJson['images'] = cachedImgs
        else:
            for entry in finalPreJson['images']:
                cachedImgs.append(entry)
            finalPreJson['images'] = cachedImgs  

    # Before returning write results to memcache
    data = memcache.get('artistImages' + artistName)
    if data is not None:
        memcache.set('artistImages' + artistName, finalPreJson['images'], 604800)
    else:
        memcache.add('artistImages' + artistName, finalPreJson['images'], 604800)


    # Encode final dictionary into json and return it
    finalJson = json.dumps(finalPreJson)
    return finalJson

""" --- """


""" This section of code which ends with a "---" block defines the method that recieves
    an artist id as an input and outputs link to an optimal size image. There is an optional second and third
    argument for the min hieght and width for an image. default is 300x300"""
def writeToBlob(artistName, imgUrl, imgLic, imgRPC, rpc, imgCnt = 0, artistId = '', minWidth = 300, minHeight = 300, maxImpWidth = 1200, maxImpHeight = 1200, maxWidth = 800, maxHeight = 600):
# Initiallize the dictionary that will eventually be converted to json
# Encode results into unicode which can be parsed by Echonest API 

    finalImgRslt = ''
# Perform check for optimal size image
    imgRet = {}
    imgUrlRslt = ''
    imgBlobRslt = {'imgUrl': '', 'reducedUrl' : '', 'license' : {}, 'thumbUrl' : ''}
    imgBlobThmbRslt = ''

    imgFile = models.ArtistImages(artistName = artistName)
    imgFile.dateAdded = datetime.utcnow().date()
    imgFile.artistEchoId = artistId
    imgFile.artistOrigImgUrl = imgUrl
    imgFile.artistImgNum = imgCnt + 1

    imgFile.artistImg = db.Blob(imgRPC)
    
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
            imgFile.artistImgBlobKey = str(imgBlobKey)
            imgFile.artistImgUrl = images.get_serving_url(imgBlobKey)
            if imgBlobRslt['imgUrl'] == '':
                imgBlobRslt['imgUrl'] = imgFile.artistImgUrl
                rpcUrlArr[rpc]['imgUrl'] = imgFile.artistImgUrl
            imgFile.artistImgLicense = imgLic
            rpcUrlArr[rpc]['license'] = imgLic


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
                if imgBlobRslt['reducedUrl'] == '':
                    imgBlobRslt['reducedUrl'] = imgFile.artistReducedImgUrl
                    rpcUrlArr[rpc]['reducedUrl'] = imgFile.artistImgUrl 
            else:
                imgBlobRslt['reducedUrl'] = imgFile.artistImgUrl
                rpcUrlArr[rpc]['reducedUrl'] = imgFile.artistImgUrl 


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
            imgFile.artistThmbBlobKey = str(imgBlobKey)
            imgFile.artistThmbUrl = images.get_serving_url(imgBlobKey)
            if imgBlobRslt['thumbUrl'] == '':
                imgBlobRslt['thumbUrl'] = imgFile.artistThmbUrl
                rpcUrlArr[rpc]['thumbUrl'] = imgFile.artistThmbUrl 

            imgFile.put()
            imgCnt = imgCnt + 1
    except Exception, error:

        imgBlobRslt = {'imgUrl': error, 'reducedUrl' : '', 'license' : {}, 'thumbUrl' : ''}


    return imgBlobRslt

""" --- """

""" Section ending with "---" defines checks to see if an entry already exists for the image requested"""
def chkExists(url):

    if len(url)> 500:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
        
    result = models.ArtistImages.gql("WHERE artistOrigImgUrl = :1 LIMIT 1", url).fetch(1)

    if (len(result) > 0):
        try:
            if result[0].artistImgLicense:
                imgLic = result[0].artistImgLicense
            else:
                imgLic = {}
            return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                    'license': imgLic, 'thumbUrl': result[0].artistThmbUrl}
        except Exception, error:
            #print error
            if result[0].artistImgUrl:
                return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                        'license': {}, 'thumbUrl': result[0].artistThmbUrl}
            else:
                return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
    else:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}

""" --- """

""" Section ending with "---" defines checks to see if an entry already exists for the image requested"""
def chkExistsLic(entry):

    if len(entry['url'])> 500:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
        
    result = models.ArtistImages.gql("WHERE artistOrigImgUrl = :1 LIMIT 1", entry['url']).fetch(1)

    if (len(result) > 0):
        try:
            if result[0].artistImgLicense:
                imgLic = result[0].artistImgLicense
                if imgLic == {}:
                    imgLic['url'] = entry['license']['url']
                    imgLic['type'] = entry['license']['type']
                    imgLic['attribution'] = entry['license']['attribution']
                    result[0].artistImgLicense = imgLic
                    result[0].put()
            else:
                imgLic = {}
                imgLic['url'] = entry['license']['url']
                imgLic['type'] = entry['license']['type']
                imgLic['attribution'] = entry['license']['attribution']
                result[0].artistImgLicense = imgLic
                result[0].put()

            if not result[0].dateAdded:
                result[0].dateAdded = datetime.utcnow().date()
                result[0].put()
            #return result[0].dateAdded
        
            return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                    'license': imgLic, 'thumbUrl': result[0].artistThmbUrl}
        except Exception, error:
            return error
            if result[0].artistImgUrl:
                return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                        'license': {}, 'thumbUrl': result[0].artistThmbUrl}
            else:
                return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
    else:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}

""" --- """

""" Section ending with "---" defines checks to see if an entry already exists for the image requested"""
def chkDBExists(url):

    if len(url)> 500:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}

    result = models.ArtistImages.gql("WHERE artistImgUrl = :1 LIMIT 1", url).fetch(1)

    if (len(result) > 0):
        try:
            if result[0].artistImgLicense:
                imgLic = result[0].artistImgLicense
            else:
                imgLic = {}
            return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                    'license': result[0].artistImgLicense,'thumbUrl': result[0].artistThmbUrl}
        except Exception, error:
            if result[0].artistImgUrl:
                return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                        'license': {}, 'thumbUrl': result[0].artistThmbUrl}
            else:
                return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
    else:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}

""" --- """

""" Section ending with "---" defines checks to see if an entry already exists for the image requested"""
def chkDBExistsLic(entry):

    if len(entry['url'])> 500:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
    
    result = models.ArtistImages.gql("WHERE artistImgUrl = :1 LIMIT 1", entry['url']).fetch(1)

    if (len(result) > 0):
        try:
            if result[0].artistImgLicense:
                imgLic = result[0].artistImgLicense
            else:
                imgLic = {}
            return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                    'license': result[0].artistImgLicense,'thumbUrl': result[0].artistThmbUrl}
        except Exception, error:
            if result[0].artistImgUrl:
                return {'imgUrl': result[0].artistImgUrl, 'reducedUrl': result[0].artistReducedImgUrl,
                        'license': {}, 'thumbUrl': result[0].artistThmbUrl}
            else:
                return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}
    else:
        return {'imgUrl': '', 'license': {}, 'thumbUrl': '', 'reducedUrl': ''}

""" --- """

""" Section ending with "---" defines checks to see if an entry already exists for the image requested"""
def chkImgCnt(artist):

    result = models.ArtistImages.gql("WHERE artistName = :1 LIMIT 100", artist).fetch(100)

    return len(result)

""" --- """

""" Section ending with "---" defines checks to see if an entry already exists for the image requested"""
def chk7DayImgCnt(artist):

    results = models.ArtistImages.gql("WHERE artistName = :1 LIMIT 100", artist).fetch(100)
    img7Cnt = 0
    imgTotCnt = 0
    if (len(results) > 0):
        try:
            todaysDate = datetime.utcnow().date()
            for entry in results:
                imgTotCnt += 1
                manuallyAdded = False
                if entry.artistImgLicense:
                    tmpLic = entry.artistImgLicense
                    if tmpLic.has_key('type'):
                        if tmpLic['type']:
                            if tmpLic['type'] == 'Manually Replaced' or tmpLic['type'] == 'Manually Added':
                                img7Cnt += 1
                                manuallyAdded = True

                if not manuallyAdded and entry.dateAdded:
                    tdelta = todaysDate - entry.dateAdded
                    if tdelta.days < 7:
                        #return 'The image for ' + entry.artistName + ' was added ' + str(tdelta.days) + ' day(s) ago'
                        img7Cnt += 1
                    
                
        except Exception, error:
            return error

    retCnt = {'under7days' : img7Cnt, 'totalImgCount' : imgTotCnt}
    return retCnt
    #return str(img7Cnt) + ' images under 7 days out of ' + str(imgTotCnt)

""" --- """

""" Section ending with "---" defines checks to see if an thumbnail exists for the artist requested"""
def getThumb(artistName):
    artistName = artistName.encode('utf-8')
    artistName = urllib.quote_plus(artistName)

    result = models.ArtistImages.gql("WHERE artistName = :1 LIMIT 1", artistName).fetch(1)

    if (len(result) > 0):
        return result[0].artistThmbUrl
    else:
        return None

""" --- """

""" Section ending with "---" defines checks to see if an thumbnail exists for the artist requested"""
def getManuallyStored(artistName):
    imgReturn = []

    imgResults = models.ArtistImages.gql("WHERE artistName = :1 LIMIT 10", artistName).fetch(10)

    for entry in imgResults:
        if entry.artistImgLicense:
            tmpLic = entry.artistImgLicense
            if tmpLic.has_key('type'):
                if tmpLic['type']:
                    if tmpLic['type'] == 'Manually Replaced' or tmpLic['type'] == 'Manually Added':
                        tmpLic['thumbnail'] = entry.artistThmbUrl
                        if entry.artistReducedImgUrl:
                            if entry.artistReducedImgUrl != '':
                                tmpReduced = entry.artistReducedImgUrl
                            else:
                                tmpReduced = entry.artistImgUrl
                        else:
                            tmpReduced = entry.artistImgUrl
                            
                        addEntry = {'url': entry.artistImgUrl, 'reduced': tmpReduced, 'license': tmpLic}
                        imgReturn.append(addEntry)
        
    return imgReturn

""" --- """ 


""" Section ending with "---" defines code that handles exceptions when making urlfetch requests"""
def RetryUrlFetch(url, counter = 0, maxTries = 3):
    try:
        loadedFetch = urlfetch.Fetch(url)
    except urlfetch.Error:
        if counter < maxTries:
            counter += 1
            return RetryUrlFetch(url, counter)
        else:
            return []
    return loadedFetch

""" --- """


""" Section ending with "---" defines class that handles background image requests"""
class BackgroundHandler(webapp.RequestHandler):
    def get(self, artist):
# Use GetArtistBackground method to obtain json data for the given artist
        backgroundJson = GetArtistBackground(self.request.get("artist"))

# Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(backgroundJson)
""" --- """



# URL to source file mappings
application = webapp.WSGIApplication([('/v1/backgrounds(.*)', BackgroundHandler),],
                                       debug=True)



""" Main function which handles url mapping"""
def main():

    
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()

