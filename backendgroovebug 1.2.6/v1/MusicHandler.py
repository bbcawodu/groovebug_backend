# -*- coding: utf-8 -*-
""" This Handler is responsible for making the API calls to iTunes, parsing the
    json data for a given artist, creating our own json formatted list of singles
    and list of albums, and returning it when queried using our internal API
    the wrapper for music will be
    http://backendgroovebug.appspot.com/v1/music?artist=
    Update- now has a caching system that holds keys in memory for 1 day.
    the key for the given artist is 'iTunesMusic' + artistName"""


import os, logging
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import webapp
from google.appengine.api import urlfetch, memcache
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
from operator import itemgetter, attrgetter
import urllib2, urllib, re, datetime
from datetime import datetime as datetimedos
import DataModels as models



""" This function recieves an artist name as an input and outputs a list of singles
    and list of albums for the given artist. There is are optional arguments for
    maximum number of singles returned, albums returned, and retries for loading
    a json document from a given URL"""
def GetArtistMusic(artist, userId = 'groovebug', maxSingles = 50):
    artist = artist.encode('utf-8')
## Initiallize the dictionary that will eventually be converted to json
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0'}
    finalPreJson['status']['comments'] = []
    finalPreJson['albums'] = []
    finalPreJson['add local'] = 'false'
    totalTrackCount = 0
    specialCase = False

    if artist == 'AM & Shawn Lee':
        artist = 'AM'
        specialCase = True

## Use API to search for artist's iTunes ID
    searchBase = 'http://itunes.apple.com/search?'
    searchArgs = {'media' : 'music',
                  'country' : 'us',
                  'entity' : 'musicArtist',
                  'attribute' : 'artistTerm',
                  'limit' : '200',}
    searchHelper = models.UrlFetchHelper(searchBase, searchArgs)
    artistIdJson = searchHelper.MakeSyncJsonFetch('term', artist)
    
# Try loading Json doc from URL, if loading times out, try again up to
# 'maxLookupRetry' times
    if artistIdJson == []:
        finalPreJson['status']['error'] = searchHelper.syncUrls[searchHelper.syncFetchIndex] + ' has timed out'
        return finalPreJson

## Return blank arrays for albums and singles if artist isnt found    
    if artistIdJson['resultCount'] == 0:
        finalPreJson['status']['error'] = 'artist not found'
        return finalPreJson

## Perform lookup of singles for given artist and append results to the singles list
    artistiTunesIds = []
    
    for result in artistIdJson['results']:
        if result['artistName'] == artist or result['artistName'].lower() == artist.lower():
            iTunesId = str(result['artistId'])
            artistiTunesIds.append(iTunesId)
            
    if artistiTunesIds == []:
        for result in artistIdJson['results']:
            if artistIdJson['results'][0]['artistName'] == result['artistName']:
                iTunesId = str(result['artistId'])
                artistiTunesIds.append(iTunesId)
    
    searchHelper.searchBase = 'http://itunes.apple.com/lookup?'
    searchHelper.searchArgs = {'entity' : 'song',
                               'country' : 'us',
                               'limit' : '200',}
    searchHelper.MakeAsyncJsonFetch('id', artistiTunesIds)
    
    for index, artistId in enumerate(artistiTunesIds):
        if totalTrackCount > 1500:
            break
        searchHelper.searchArgs = {'entity' : 'album',
                                   'country' : 'us',
                                   'limit' : '200',}
        albumData = searchHelper.MakeSyncJsonFetch('id', artistId)
        ourAlbumsData = []
        albumIds = []
        
        if albumData == []:
            finalPreJson['status']['comments'].append(searchHelper.syncUrls[searchHelper.syncFetchIndex] + ' timed out')
            break
        albumSongsQuery = ''
        numberOfAlbums = 0
        searchHelper.searchArgs = {'entity' : 'song',
                                   'country' : 'us',
                                   'limit' : '200',}
        for indexAlbum, entry in enumerate(albumData['results']):
            if totalTrackCount >= 1550:
                break
            if entry['wrapperType'] == 'collection':
                numberOfAlbums += 1
                albumIdIndex = {}
                album = {}
                albumIdIndex['iTunesAlbumId'] = str(entry['collectionId'])
                albumIdIndex['trackCount'] = album['trackCount'] = int(entry['trackCount'])
                albumIdIndex['title'] = album['title'] =  album['title(original)'] = entry['collectionName']
                if entry['collectionExplicitness'] == 'cleaned':
                    album['title'] = album['title(original)'] + ' (Clean)'
                else:
                    album['title(original)'] = ''
                album['artist'] = entry['artistName']
                album['thumbnail'] = entry['artworkUrl100']
                album['linkshare tracker'] = 'http://ad.linksynergy.com/fs-bin/show?id=2ykC*y*No88&bids=146261.1' + '&u1=' + userId + '&type=10'
                rawDate = entry['releaseDate']
                rawDate = re.sub('T.*$', '', rawDate)
                dateObject = datetimedos.strptime(rawDate, '%Y-%m-%d')
                dateString = dateObject.strftime('%b %d, %Y')
                album['date'] = dateString
                rawBuyLink = entry['collectionViewUrl']
                if re.search('\?', rawBuyLink):
                    rawBuyLink = rawBuyLink + '&' + 'partnerId=30'
                else:
                    rawBuyLink = rawBuyLink + '?' + 'partnerId=30'
                rawBuyLink = urllib.quote_plus(rawBuyLink)
                rawBuyLink = urllib.quote_plus(rawBuyLink)
                ourBuyLink = 'http://click.linksynergy.com/fs-bin/click?id=2ykC*y*No88&subid=&offerid=146261.1&type=10&tmpid=3909' + '&u1=' + userId + '&RD_PARM1=' + rawBuyLink
                album['buy'] = ourBuyLink
                album['tracks'] = []
                albumIds.append(albumIdIndex)
                ourAlbumsData.append(album)
                albumSongsQuery = albumSongsQuery + str(entry['collectionId'])
                if numberOfAlbums%10 == 0 or indexAlbum+1 == albumData['resultCount']:
                    albumSongsData = searchHelper.MakeSyncJsonFetch('id', albumSongsQuery)
                    try:
                        albumSongsResults = albumSongsData['results']
                    except Exception:
                        finalPreJson['status']['comments'].append(searchHelper.syncUrls[searchHelper.syncFetchIndex] + ' timed out')
                        break
                    trackCounter = 0
                    for albumIndex, idEntry in enumerate(albumIds):
                        trackDifference = 'no'
                        if albumIndex == 0:
                            if not idEntry['trackCount'] == albumSongsResults[trackCounter]['trackCount']:
                                numberOfTracks = albumSongsResults[trackCounter]['trackCount']
                                ourAlbumsData[albumIndex]['trackCount'] = albumSongsResults[trackCounter]['trackCount']
                            else: 
                                numberOfTracks = idEntry['trackCount']
                            trackCounter +=1
                        if trackCounter > len(albumSongsResults)-1:
                            track = {'error' : 'there are no tracks available in iTunes'}
                            ourAlbumsData[albumIndex]['tracks'].append(track)
                            break
                        else:
                            if albumSongsResults[trackCounter]['wrapperType'] == 'track':
                                for trackIndex in range(numberOfTracks):
                                    track = {}
                                    if trackCounter > len(albumSongsResults)-1:
                                        ourAlbumsData[albumIndex]['trackCount'] = albumSongsResults[trackCounter-1]['trackNumber']
                                        break
                                    if not albumSongsResults[trackCounter].has_key('trackNumber'):
                                        trackDifference = 'yes'
                                        trackDifferenceNumber = trackIndex
                                        break
                                    track['number'] = albumSongsResults[trackCounter]['trackNumber']
                                    track['artist'] = albumSongsResults[trackCounter]['artistName']
                                    track['title'] = '(Preview) ' + albumSongsResults[trackCounter]['trackName']
                                    track['preview'] = albumSongsResults[trackCounter]['previewUrl']
                                    track['source'] = 'preview'
                                    rawBuyLink = albumSongsResults[trackCounter]['trackViewUrl']
                                    if re.search('\?', rawBuyLink):
                                        rawBuyLink = rawBuyLink + '&' + 'partnerId=30'
                                    else:
                                        rawBuyLink = rawBuyLink + '?' + 'partnerId=30'
                                    rawBuyLink = urllib.quote_plus(rawBuyLink)
                                    rawBuyLink = urllib.quote_plus(rawBuyLink)
                                    ourBuyLink = 'http://click.linksynergy.com/fs-bin/click?id=2ykC*y*No88&subid=&offerid=146261.1&type=10&tmpid=3909' + '&u1=' + userId + '&RD_PARM1=' + rawBuyLink
                                    track['buy'] = ourBuyLink
                                    trackTime = datetime.timedelta(seconds = (int(albumSongsResults[trackCounter]['trackTimeMillis'])/1000))
                                    trackTime = str(trackTime)
                                    trackTime = list(trackTime)
                                    if trackTime[0] == '0':
                                        del trackTime[0]
                                        del trackTime[0]
                                        if trackTime[0] == '0':
                                            del trackTime[0]
                                        trackTime = ''.join(trackTime)
                                    else:
                                        trackTime = ''.join(trackTime)
                                    track['length'] = trackTime
                                    ourAlbumsData[albumIndex]['tracks'].append(track)
                                    trackCounter += 1
                                    totalTrackCount += 1
                                if trackDifference == 'yes':
                                    ourAlbumsData[albumIndex]['trackCount'] = trackDifferenceNumber
                                if not albumIndex == len(albumIds) - 1:
                                    if not albumIds[albumIndex+1]['trackCount'] == albumSongsResults[trackCounter]['trackCount']:
                                        numberOfTracks = albumSongsResults[trackCounter]['trackCount']
                                        ourAlbumsData[albumIndex+1]['trackCount'] = albumSongsResults[trackCounter]['trackCount']
                                    else: 
                                        numberOfTracks = albumIds[albumIndex+1]['trackCount']
                            elif albumSongsResults[trackCounter]['wrapperType'] == 'collection':
                                track = {'error' : 'there are no tracks available in iTunes'}
                                ourAlbumsData[albumIndex]['tracks'].append(track)
                                if not albumIndex == len(albumIds) - 1:
                                    if not albumIds[albumIndex+1]['trackCount'] == albumSongsResults[trackCounter]['trackCount']:
                                        numberOfTracks = albumSongsResults[trackCounter]['trackCount']
                                        ourAlbumsData[albumIndex+1]['trackCount'] = albumSongsResults[trackCounter]['trackCount']
                                    else: 
                                        numberOfTracks = albumIds[albumIndex+1]['trackCount']
                        trackCounter += 1
                        
                    for entry in ourAlbumsData:
                        if specialCase == True:
                            if artist == 'AM & Shawn Lee':
                                finalPreJson['albums'].append(entry)
                        else:
                            finalPreJson['albums'].append(entry)
                    if numberOfAlbums%10 == 0:
                        ourAlbumsData = []
                        albumIds = []
                        albumSongsQuery = ''
                else:
                    albumSongsQuery = albumSongsQuery + ','

    allSingles= []
    singlesData = searchHelper.RetrieveAsyncData()   
    for entry in singlesData:
        for singleEntry in entry['results']:    
            if singleEntry['wrapperType'] == 'track':
                single = {}
                single['title'] = '(Preview) ' + singleEntry['trackName']
                single['artist'] = singleEntry['artistName']
                single['number'] = ''
                single['preview'] = singleEntry['previewUrl']
                single['source'] = 'preview'
                rawBuyLink = singleEntry['trackViewUrl']
                if re.search('\?', rawBuyLink):
                    rawBuyLink = rawBuyLink + '&' + 'partnerId=30'
                else:
                    rawBuyLink = rawBuyLink + '?' + 'partnerId=30'
                rawBuyLink = urllib.quote_plus(rawBuyLink)
                rawBuyLink = urllib.quote_plus(rawBuyLink)
                ourBuyLink = 'http://click.linksynergy.com/fs-bin/click?id=2ykC*y*No88&subid=&offerid=146261.1&type=10&tmpid=3909' + '&u1=' + userId + '&RD_PARM1=' + rawBuyLink
                single['buy'] = ourBuyLink
                trackTime = datetime.timedelta(seconds = (int(singleEntry['trackTimeMillis'])/1000))
                trackTime = str(trackTime)
                trackTime = list(trackTime)
                if trackTime[0] == '0':
                    del trackTime[0]
                    del trackTime[0]
                    if trackTime[0] == '0':
                        del trackTime[0]
                    trackTime = ''.join(trackTime)
                else:
                    trackTime = ''.join(trackTime)
                single['length'] = trackTime
                if specialCase == True:
                    if artist == 'AM' and single['artist'] == 'AM & Shawn Lee':
                        myThumbnail = singleEntry['artworkUrl100']
                        myTitle = singleEntry['collectionName']
                        myDate = singleEntry['releaseDate']
                        myBuy = singleEntry['collectionViewUrl']
                        allSingles.append(single)
                else:
                    allSingles.append(single)

    singlesAlbum = []    
    for single in allSingles:
        needThisSingle = 'yes'
        for album in finalPreJson['albums']:
            for track in album['tracks']:
                if single.has_key('preview') and track.has_key('preview'):
                    if track['preview'] == single['preview']:
                        needThisSingle = 'no'

        if needThisSingle == 'yes':
            singlesAlbum.append(single)

    if not singlesAlbum == [] and totalTrackCount <= 1550:
        singlesAlbumEntry = {}
        if specialCase == True:
            if artist == 'AM':
                singlesAlbumEntry['title'] = myTitle
                rawBuyLink = myBuy
                if re.search('\?', rawBuyLink):
                    rawBuyLink = rawBuyLink + '&' + 'partnerId=30'
                else:
                    rawBuyLink = rawBuyLink + '?' + 'partnerId=30'
                rawBuyLink = urllib.quote_plus(rawBuyLink)
                rawBuyLink = urllib.quote_plus(rawBuyLink)
                ourBuyLink = 'http://click.linksynergy.com/fs-bin/click?id=2ykC*y*No88&subid=&offerid=146261.1&type=10&tmpid=3909' + '&u1=' + userId + '&RD_PARM1=' + rawBuyLink
                singlesAlbumEntry['buy'] = ourBuyLink
                singlesAlbumEntry['artist'] = singlesAlbum[0]['artist']
                singlesAlbumEntry['thumbnail'] = myThumbnail
                rawDate = myDate
                rawDate = re.sub('T.*$', '', rawDate)
                dateObject = datetimedos.strptime(rawDate, '%Y-%m-%d')
                dateString = dateObject.strftime('%b %d, %Y')
                singlesAlbumEntry['date'] = dateString
        else:
            singlesAlbumEntry['buy'] = 'N/A'
            singlesAlbumEntry['title'] = 'Singles'
            singlesAlbumEntry['artist'] = artist
            singlesAlbumEntry['thumbnail'] = 'http://backendgroovebug.appspot.com/htmlimages/groovebugicon.png'
            singlesAlbumEntry['date'] = 'Misc.'
        singlesAlbumEntry['tracks'] = []
        for single in singlesAlbum:
            if totalTrackCount > 1600:
                break
            singlesAlbumEntry['tracks'].append(single)
            totalTrackCount += 1
        singlesAlbumEntry['trackCount'] = len(singlesAlbumEntry['tracks'])
        finalPreJson['albums'].append(singlesAlbumEntry)

    for entry in searchHelper.asyncUrlErrors:
        finalPreJson['status']['comments'].append(entry + ' timed out')
 
    if finalPreJson['albums'] == []:
        finalPreJson['status']['error'] = 'Sorry, no music available.'
    
# Return final dictionarty
    return finalPreJson
""" --- """



def getCachedMusic(artist , user = 'groovebug'):
    if user == 'unit-tests':
        data = memcache.get('iTunesMusicTest' + artist)
    else:
        data = memcache.get('iTunesMusic' + artist)
    if data is not None:
        if data['status']['error'] != '0' or data['albums'] == [] or data['status']['comments'] != []:
           data = GetArtistMusic(artist, userId = user)
           if not len(str(data)) > 1000000:
               memcache.set('iTunesMusic' + artist, data, 86400)
        return data
    else:
        data = GetArtistMusic(artist, userId = user)
        if not len(str(data)) > 1000000:
            memcache.add('iTunesMusic' + artist, data, 86400)
        return data


def getPromoMusic(artist):
    #artist = artist.encode('utf-8')
    artistEnc = artist.encode('utf-8')
    artistName = urllib.quote_plus(artistEnc)
    #logMsg = 'Getting Promo Music for artist - ' + artistName
    #logging.info(logMsg)
## Initialize list that will contain dictionary entries with audio data
    audio = []
    newUserAlbums = {}
    newUserAlbums['albums'] = []
    newUserAlbum = {}
    #audioRec = models.PromotedAudio(artistName = artistName)
    audioRec = models.PromotedAudio.gql("WHERE artistName = :1 ORDER BY album, trackNum LIMIT 20", artistName).fetch(20)
    #logMsg = 'There were ' + str(len(audioRec)) + ' record(s) found for artist - ' + artistName
    #logging.info(logMsg)
    if len(audioRec) > 0:
        currAlbum = 'zxcvb'
        
        lastTrkNum = 0
        featStr = '⇝Featured⇜'
        featStr = featStr.decode('utf-8')
        for i, aEntry in enumerate(audioRec):
            if aEntry.album != currAlbum:
                if newUserAlbum != {}:
                    newUserAlbums['albums'].append(newUserAlbum)
                currAlbum = aEntry.album
                newUserAlbum = {}
                if aEntry.album != '':
                    newUserAlbum['title'] = featStr + ' ' + aEntry.album
                else:
                    newUserAlbum['title'] = featStr
                newUserAlbum['artist'] = artist
                if aEntry.buyUrl:
                    newUserAlbum['buy'] = aEntry.buyUrl
                else:
                    newUserAlbum['buy'] = 'http://' + str(hostUrl) + '/artist/missingbuy'
                newUserAlbum['linkshare tracker'] = 'http://ad.linksynergy.com/fs-bin/show?id=2ykC*y*No88&bids=146261.1&u1=groovebug&type=10'
                newUserAlbum['trackCount'] = 0
                newUserAlbum['date'] = ''
                newUserAlbum['thumbnail'] = aEntry.thumbUrl
                newUserAlbum['tracks'] = []

            newUserTrk = {}
            newUserAlbum['trackCount'] += 1
            if aEntry.buyUrl:
                newUserTrk['buy'] = aEntry.buyUrl
            else:
                newUserTrk['buy'] = 'http://' + str(hostUrl) + '/artist/missingbuy'
            #newUserTrk['buy'] = 'Promo'
            newUserTrk['source'] = 'promo'
            newUserTrk['artist'] = artist
            newUserTrk['title'] = featStr + ' ' + aEntry.title
            if aEntry.trackNum:
                newUserTrk['number'] = aEntry.trackNum
            else:
                if (lastTrkNum + 1) > newUserAlbum['trackCount']:
                    newUserTrk['number'] = lastTrkNum + 1
                else:
                    newUserTrk['number'] = newUserAlbum['trackCount']
            lastTrkNum = int(newUserTrk['number'])
            newUserTrk['preview'] = aEntry.url
            newUserAlbum['tracks'].append(newUserTrk)

        if newUserAlbum != {}:
            newUserAlbums['albums'].append(newUserAlbum)

    return newUserAlbums      
            

""" Section ending with "---" defines a function that replaces the albums and songs from the fetched
    call with matches from the user's library"""

def replaceUserData(userData, fetchedData):
    newUserData = {}
    newUserData['status'] = {'version': "1.0", 'comments': [], 'error': "0"}
    newUserData['albums'] = []
    newUserData['add local'] = 'false'
    currAlbum = 'zxcvb'
    currArtist = 'zxcvb'
    albumFound = False
    newUserAlbum = {}
    for uEntry in userData:
        if uEntry.has_key('url'):
            if uEntry['album'].lower() != currAlbum.lower() or uEntry['artist'].lower() != currArtist.lower():
                if newUserAlbum != {}:
                    newUserData['albums'].append(newUserAlbum)
                newUserAlbum = {}
                currAlbum = uEntry['album']
                currArtist = uEntry['artist']
                for fAEntry in fetchedData['albums']:
                    if uEntry['album'].lower() == fAEntry['title'].lower():
                        #newUserAlbum = fAEntry
                        newUserAlbum['title'] = uEntry['album']
                        newUserAlbum['title(original)'] = uEntry['album']
                        newUserAlbum['artist'] = uEntry['artist']
                        newUserAlbum['buy'] = 'Already Owns'
                        newUserAlbum['linkshare tracker'] = 'http://ad.linksynergy.com/fs-bin/show?id=2ykC*y*No88&bids=146261.1&u1=groovebug&type=10'
                        newUserAlbum['trackCount'] = 0
                        newUserAlbum['date'] = fAEntry['date']
                        newUserAlbum['thumbnail'] = fAEntry['thumbnail']
                        newUserAlbum['tracks'] = []
                        if not len(fAEntry['tracks']) > 0:
                            fetchedData['albums'].remove(fAEntry)
                        albumFound = True
                        break
                       
                if newUserAlbum == {}:
                    albumFound = False
                    newUserAlbum['title'] = uEntry['album']
                    newUserAlbum['title(original)'] = uEntry['album']
                    newUserAlbum['artist'] = uEntry['artist']
                    newUserAlbum['buy'] = 'Already Owns'
                    newUserAlbum['linkshare tracker'] = 'http://ad.linksynergy.com/fs-bin/show?id=2ykC*y*No88&bids=146261.1&u1=groovebug&type=10'
                    newUserAlbum['trackCount'] = 0
                    newUserAlbum['date'] = ''
                    newUserAlbum['thumbnail'] = 'http://' + str(hostUrl) + '/htmlimages/cd_icon.jpg'
                    newUserAlbum['tracks'] = []
              
            #trkFound = False
            newUserTrk = {}
            newUserAlbum['trackCount'] += 1
            newUserTrk['buy'] = 'Already Owns'
            newUserTrk['source'] = 'local'
            newUserTrk['artist'] = uEntry['artist']
            newUserTrk['title'] = uEntry['title']
            newUserTrk['number'] = uEntry['track number']
            a,b = divmod(uEntry['duration'], 60)
            if b > 9:
                newUserTrk['length'] = str(int(a)) + ':' + str(int(b))
            else:
                newUserTrk['length'] = str(int(a)) + ':0' + str(int(b))
            
            newUserTrk['preview'] = uEntry['url']

            for fEntry in fetchedData['albums']:
                if uEntry['album'].lower() == fEntry['title'].lower():
                    #newUserAlbum['thumbnail'] = fEntry['thumbnail']
                    for tEntry in fEntry['tracks']:
                        titleTest = re.sub(r'\(Preview\) ', '', tEntry['title'])
                        if uEntry['title'].lower() == titleTest.lower():
                        #if uEntry['title'].lower() == titleTest.lower() and uEntry['track number'] == tEntry['number']:
                            newUserTrk['number'] = tEntry['number']
                            #fEntry['tracks'].remove(tEntry)
                            #fEntry['trackCount'] = fEntry['trackCount'] - 1
                            if not len(fEntry['tracks']) > 0:
                                fetchedData['albums'].remove(fEntry)
                            break
                            break
                            
            newUserAlbum['tracks'].append(newUserTrk)

    if newUserAlbum != {}:
        newUserData['albums'].append(newUserAlbum)

    newUserData['albums'].extend(fetchedData['albums'])

    return newUserData

""" --- """

""" Section ending with "---" defines a function that replaces the albums and songs from the fetched
    call with matches from the user's library"""

def removePromoDups(promoAlbums, fetchedData):
    removedDupData = []
    currAlbum = 'zxcvb'
    currArtist = 'zxcvb'
    albumFound = False
    featStr = '⇝Featured⇜'
    featStr = featStr.decode('utf-8')
    #return promoAlbums
    for pAEntry in promoAlbums['albums']:
        pATitleTest = re.sub(featStr, '', pAEntry['title'])
        pATitleTest = pATitleTest.strip()
        for fAEntry in fetchedData['albums']:
            if fAEntry['title'].lower() == pATitleTest.lower():
                for pTEntry in pAEntry['tracks']:
                    pTitleTest = re.sub(featStr, '', pTEntry['title'])
                    pTitleTest = pTitleTest.strip()
                    for fTEntry in fAEntry['tracks']:
                        if fTEntry['source'] == 'preview':
                            fTitleTest = re.sub(r'\(Preview\) ', '', fTEntry['title'])
                            if fTitleTest.lower() == pTitleTest.lower():
                                fAEntry['tracks'].remove(fTEntry)
                                fAEntry['trackCount'] = fAEntry['trackCount'] - 1
                                if not len(fAEntry['tracks']) > 0:
                                    fetchedData['albums'].remove(fAEntry)



    return fetchedData

""" --- """
    
""" Section ending with "---" defines class that handles music requests"""
class MusicHandler(webapp.RequestHandler):
    def get(self, artist):
## Use getCachedMusic method to obtain music data for the given artist
        artist = self.request.get("artist")
        if not artist == '':
            currentUserId = self.request.get("user")
            currentUserId = currentUserId.encode('utf-8')
            musicData = getCachedMusic(artist, user = currentUserId)
        else:
            musicData = getCachedMusic(artist)

        promoMusicData = getPromoMusic(artist)

        musicFinalAlbums =  []
        musicFinalAlbums.extend(promoMusicData['albums'])
        if len(promoMusicData['albums']) > 0:
            removedDupAlbums = removePromoDups(promoMusicData, musicData)
            musicFinalAlbums.extend(removedDupAlbums['albums'])
        else:
            musicFinalAlbums.extend(musicData['albums'])
        musicData['albums'] = musicFinalAlbums
        musicJson = json.dumps(musicData, separators=(',',':'))

## Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(musicJson)
        
    def post(self, artist):
        loadedData = json.load(self.request.body_file)
        sortedUserData = sorted(loadedData['songs'], key=itemgetter('artist', 'album', 'track number'))
        sortedUserJson = json.dumps(sortedUserData, separators=(',',':'))
        artist = self.request.get("artist")
## Use getCachedMusic method to obtain music data for the given artist
        if not self.request.get('user') == '':
            currentUserId = self.request.get("user")
            currentUserId = currentUserId.encode('utf-8')
            
            musicData = getCachedMusic(artist, user = currentUserId)
        else:
            musicData = getCachedMusic(artist)
            
        promoMusicData = getPromoMusic(artist)
        musicReplData = replaceUserData(sortedUserData, musicData)
        #musicReplJson = json.dumps(musicReplData, separators=(',',':'))
            
        musicFinalAlbums =  []
        musicFinalAlbums.extend(promoMusicData['albums'])
        if len(promoMusicData['albums']) > 0:
            removedDupAlbums = removePromoDups(promoMusicData, musicReplData)
            musicFinalAlbums.extend(removedDupAlbums['albums'])
        else:
            musicFinalAlbums.extend(musicReplData['albums'])
        musicReplData['albums'] = musicFinalAlbums
        musicJson = json.dumps(musicReplData, separators=(',',':'))

## Set the html content type to 'application/json' for json viewers
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(musicJson)
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/music(.*)', MusicHandler),],
                                       debug=True)
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
