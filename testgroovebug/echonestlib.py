# -*- coding: utf-8 -*-
""" This file is a library of echonest methods for accessing
    various information from their server"""
import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import db, deferred
from google.appengine.api import urlfetch, memcache
from google.appengine.runtime import DeadlineExceededError
import json
import DataModels as models
from operator import itemgetter, attrgetter
import urllib2, urllib, datetime, re, htmlentitydefs, logging, unicodedata, datetime, time
logging.getLogger().setLevel(logging.DEBUG)

if str(hostUrl) == 'backendgroovebug.appspot.com':
    APIKEY = '269A92REW5YH3KNZW'
elif str(hostUrl) == 'testgroovebug.appspot.com':
    APIKEY = 'GN7EUP6EYOFTT75NN'
else:
    APIKEY = 'GN7EUP6EYOFTT75NN'



class Echonest_Data_Loader():
    """ This parent class is responsible for getting various data from echonest.
    NOTES:
    -DO NOT INSTANTIATE'"""
    def __init__(self, artistList, deadline = 10, maxFails = 20):
        """ This method initializes variables that will be used by all echonest classes"""
        self.artistList = artistList
        self.failCounter = 0
        self.rpcs = []
        self.deadline = deadline
        self.maxFails = maxFails
        self.apiKey = APIKEY

    def load(self):
        """ This method takes no inputs and returns an array of echonest data
            for a given array of artists. The data is in the same order as the
            input array with None for entries not found"""
        
## log the start of the method to google app engine and initialize arrays that store
## datastore keys, and final data to be output
        retStatus = 'Finished'
        try:
            logging.info('Start getting echonest ' + self.echonestDataType + ' for ' + str(len(self.artistList)) + ' artists')
            self.datastoreLookups = []
            self.datastoreKeys = []
            self.allArtistDataList = []

    ## use memcache.get_multi() to check memcache for data asynchronously
            cachedEntries = memcache.get_multi(self.artistList, key_prefix = self.memcacheKey)
            for postIndex, artist in enumerate(self.artistList):
                artistEntry = {}
                artistEntry['index'] = postIndex
                artistEntry['artist name'] = artist
                if re.search(r'^_(_+)(.*)_(_+)$', artist) != None:
                    artistEntry['datastore key'] = re.sub(r'^_(_+)|_(_+)$', '', artist)
                else:
                    artistEntry['datastore key'] = artist

    ## make sure artist name isnt an empty string. If artist data was found in the
    ## cache, append it to final data, and if not append artist to list to be checked
    ## from datastore
                if artist != ''.encode('utf-8'):
                    if cachedEntries.has_key(artist):
                        self.appendDataFromCache(artistEntry, cachedEntries[artist])
                    else:
                        self.datastoreLookups.append(artistEntry)
                        self.datastoreKeys.append(artistEntry['datastore key'])
                else:
                    artistEntry['data'] = None
                    self.allArtistDataList.append(artistEntry)

    ## use self.datastoreLookups method to check datastore for specified data and append rpcs
    ## if not found
            if self.datastoreLookups != []:
                self.artistDataFromDatastore()

    ## launch urls and parse the results 3 at a time
            currentRPCs = []
            for index, rpc in enumerate(self.rpcs):
                urlfetch.make_fetch_call(rpc['rpc'], rpc['url'])
                currentRPCs.append(rpc['rpc'])
                if index == (len(self.rpcs) - 1) or (len(currentRPCs)%3 == 0):
                    for rpc in currentRPCs:
                        rpc.wait()
                    logging.info('Finished processing ' + str(len(currentRPCs)) + ' rpcs')
                    currentRPCs = []

        except DeadlineExceededError:
            logging.info('Timed out, but finished processing ' + str(len(self.allArtistDataList)) + ' artists')
            retStatus = 'Timed Out'
            
## sort data by the order of the inputted artist array and return it
        self.allArtistDataListFinal = []
        allArtistDataList = sorted(self.allArtistDataList, key = lambda artist: artist['index'])
        for entry in allArtistDataList:
            self.allArtistDataListFinal.append(entry['data'])
        logging.info('Finished getting echonest ' + self.echonestDataType + ' for ' + str(len(self.allArtistDataListFinal)) + ' artists')
        return self.allArtistDataListFinal

    def urlFromName(self, artist):
        """ This method takes an artist as an input and returns appropriate echonest url from artist name"""
        return self.urlWrapper + '&name=' + urllib.quote_plus(artist.encode('utf-8'))

    def appendDataFromCache(self, artistEntry, cachedData):
        """ This method takes a dictionary of data for an artist, and data found in the cache as inputs,
            adds the cached data to the dictionary, and appends dictionary to final data array"""
        artistEntry['data'] = cachedData
        self.allArtistDataList.append(artistEntry)

    def artistDataFromDatastore(self):
        """ This method takes no inputs, and adds entries found in the datastore and appends rpcs ones that are not found"""
        pass

    def appendRPC(self, artistEntry):
        """ This method takes a dictionary of data for an artist as an input, and appends a 'remote process call'
            for that artist to the list of rpcs"""
        rpc = urlfetch.create_rpc(deadline = self.deadline)
        rpc.callback = self.asyncCallback(artistEntry, rpc)
        rpcPair = {}
        rpcPair['rpc'] = rpc
        rpcPair['url'] = artistEntry['url']
        self.rpcs.append(rpcPair)

    def asyncCallback(self, artistEntry, rpc):
        """ This method takes a dictionary of data for an artist and a remote process call object as an input
            processes the remote process call, and adds the parsed data to the artist dictionary.
            NOTE: lambda extraction is used because google app engine does not allow callback functions to
                  take inputs"""
        return lambda: self.handleAsyncCallback(artistEntry, rpc)

    def handleAsyncCallback(self, artistEntry, rpc):
        """ This method is the lambda extraction of the above method. It runs all the code needed."""
        try:
            result = rpc.get_result()
            if result.status_code == 200:
                artistJson = json.loads(result.content)
                self.parseJson(artistJson, artistEntry)
            else:
                self.failCounter += 1
                if self.failCounter <= self.maxFails:
                    time.sleep(.1)
                    logging.info(str(result.status_code) + ' code on url: ' + str(artistEntry['url']) + '. Re-appending')
                    self.appendRPC(artistEntry)
                else:
                    raise Exception, "There were " + str(self.failCounter) + ' failed echonest calls, FAILURE'
        except urlfetch.DeadlineExceededError:
            self.failCounter += 1
            if self.failCounter < self.maxFails:
                time.sleep(.1)
                logging.info('urlfetch deadline exceeded error on url: ' + str(artistEntry['url']) + '. Re-appending')
                self.appendRPC(artistEntry)
            else:
                raise Exception, "There were " + str(self.failCounter) + ' failed echonest calls, FAILURE'

    def parseJson(self, artistJson, artistEntry):
        """ This method takes the parsed json data from a remote process call and a dictionary for an artist,
            adds the parsed data to the dictionary, and appends it to the final output array."""
        pass



class Echonest_Correction_Loader(Echonest_Data_Loader):
    """ This method is a subclass of Echonest_Data_Loader that is specialized for corrected artist
        names."""
    def __init__(self, artistList, deadline = 10, maxFails = 20):
        Echonest_Data_Loader.__init__(self, artistList, deadline, maxFails)
        self.memcacheKey = 'artistVerifyCache'
        self.echonestDataType = 'corrections'
        self.searchBase = 'http://developer.echonest.com/api/v4/artist/search?api_key=' + self.apiKey + '&'
        self.searchArgs = {'format' : 'json',
                      'results' : '1',
                      'fuzzy_match' : 'false',}
        self.urlWrapper = self.searchBase + str(urllib.urlencode(self.searchArgs))

    def appendDataFromCache(self, artistEntry, cachedData):
        if cachedData == "echonest has no correction for this artist":
            artistEntry['data'] = None
        else:
            artistEntry['data'] = cachedData
        self.allArtistDataList.append(artistEntry)

    def artistDataFromDatastore(self):
        datastoreEntries = models.ArtistCorrection.get_by_key_name(self.datastoreKeys)
        for index, artistEntry in enumerate(self.datastoreLookups):
            datastoreEntry = datastoreEntries[index]
            if datastoreEntry is None:
                artistEntry['url'] = self.urlFromName(artistEntry['artist name'])
                self.appendRPC(artistEntry)
            else:
                if datastoreEntry.corrected_name == "echonest has no correction for this artist":
                    artistEntry['data'] = None
                else:
                    artistEntry['data'] = datastoreEntry.corrected_name
                self.allArtistDataList.append(artistEntry)

    def parseJson(self, artistJson, artistEntry):
        if artistJson['response'].has_key('artists') and artistJson['response']['artists'] != [] and artistJson['response']['status']['code'] == 0:
            correctedName = artistJson['response']['artists'][0]['name']
        elif artistJson['response']['status']['code'] != 0:
            raise Exception, "Echonest response code is not 0. It is " + str(artistJson['response']['status']['code'])
        else:
            correctedName = 'echonest has no correction for this artist'
        if correctedName != 'echonest has no correction for this artist':
            artistEntry['data'] = correctedName
        else:
            artistEntry['data'] = None
        self.allArtistDataList.append(artistEntry)
        artistCorrectionEntry = models.ArtistCorrection(key_name = artistEntry['datastore key'], uncorrected_name = artistEntry['artist name'], corrected_name = correctedName)
        artistCorrectionEntry.put()
        memcache.set('artistVerifyCache' + artistEntry['artist name'], correctedName, 604800)



class Echonest_Similar_Artist_Loader(Echonest_Data_Loader):
    """ This method is a subclass of Echonest_Data_Loader that is specialized for similar artist
        names.
        Note: takes an extra argument maxSimilar which specifies the maximum number of similar
              artists for an individual artist"""
    def __init__(self, artistList, deadline = 10, maxFails = 20, maxSimilar = 100):
        Echonest_Data_Loader.__init__(self, artistList, deadline, maxFails)
        self.memcacheKey = 'similarArtistCache'
        self.echonestDataType = 'similar artists'
        self.maxSimilar = maxSimilar
        self.searchBase = 'http://developer.echonest.com/api/v4/artist/similar?api_key=' + self.apiKey + '&'
        self.searchArgs = {'format' : 'json',
                      'results' : '100',}
        self.urlWrapper = self.searchBase + str(urllib.urlencode(self.searchArgs))

    def appendDataFromCache(self, artistEntry, cachedData):
        artistEntry['data'] = cachedData[:self.maxSimilar]
        self.allArtistDataList.append(artistEntry)

    def artistDataFromDatastore(self):
        datastoreEntries = models.SimilarArtists.get_by_key_name(self.datastoreKeys)
        for index, artistEntry in enumerate(self.datastoreLookups):
            datastoreEntry = datastoreEntries[index]
            if datastoreEntry is None:
                artistEntry['url'] = self.urlFromName(artistEntry['artist name'])
                self.appendRPC(artistEntry)
            else:
                artistEntry['data'] = json.loads(datastoreEntry.similar_artists)[:self.maxSimilar]
                self.allArtistDataList.append(artistEntry)

    def parseJson(self, artistJson, artistEntry):
        similarArtistList = []
        if artistJson['response'].has_key('artists') and artistJson['response']['artists'] != [] and artistJson['response']['status']['code'] == 0:
            for entry in artistJson['response']['artists']:
                simArtist = entry['name']
                similarArtistList.append(simArtist)
        elif artistJson['response']['status']['code'] == 5:
            similarArtistList = []
        elif artistJson['response']['status']['code'] != 0:
            raise Exception, "Echonest response code is not 0. It is " + str(artistJson['response']['status']['code']) + ' from this url: ' + url
        else:
            similarArtistList = []
        artistEntry['data'] = similarArtistList[:self.maxSimilar]
        self.allArtistDataList.append(artistEntry)
        similarArtistEntry = models.SimilarArtists(key_name = artistEntry['datastore key'], artist_name = artistEntry['artist name'], similar_artists = json.dumps(similarArtistList))
        similarArtistEntry.put()
        memcache.set('similarArtistCache' + artistEntry['artist name'], similarArtistList, 604800)



class Echonest_News_Loader(Echonest_Data_Loader):
    """ This method is a subclass of Echonest_Data_Loader that is specialized for news articles."""
    def __init__(self, artistList, deadline = 10, maxFails = 20):
        Echonest_Data_Loader.__init__(self, artistList, deadline, maxFails)
        self.memcacheKey = 'echonestNewsCache'
        self.echonestDataType = 'news'
        self.searchBase = 'http://developer.echonest.com/api/v4/artist/news?api_key=' + self.apiKey + '&'
        self.searchArgs = {'format' : 'json',
                           'results' : '25',
                           'high_relevance' : 'true',}
        self.urlWrapper = self.searchBase + str(urllib.urlencode(self.searchArgs))

    def artistDataFromDatastore(self):
        datastoreEntries = models.EchonestNews.get_by_key_name(self.datastoreKeys)
        for index, artistEntry in enumerate(self.datastoreLookups):
            datastoreEntry = datastoreEntries[index]
            if datastoreEntry is None:
                artistEntry['url'] = self.urlFromName(artistEntry['artist name'])
                self.appendRPC(artistEntry)
            else:
                artistEntry['data'] = json.loads(datastoreEntry.news_list)
                self.allArtistDataList.append(artistEntry)

    def parseJson(self, artistJson, artistEntry):
        newsList = []
        if artistJson['response'].has_key('news') and artistJson['response']['news'] != [] and artistJson['response']['status']['code'] == 0:
            for entry in artistJson['response']['news']:
                if entry.has_key('date_posted'):
                    newsItem = {}
                    newsItem['title'] = re.sub(r'<.*?>', '', models.unescape(entry['name']))
                    newsItem['summary'] = re.sub(r'<.*?>', '', models.unescape(entry['summary']))
                    if len(newsItem['summary']) > 350:
                        newsItem['summary'] = newsItem['summary'][:350] + '...'
                    newsItem['date'] = re.sub(r'T(.*)$', '', str(entry['date_posted']))
                    newsItem['url'] = unicode(entry['url'])
                    intermsource = re.sub(r'^http(s)*(://)*(www\.)*', '', str(newsItem['url']), count = 1)
                    newsItem['articleSource'] = re.sub(r'/(.*)$', '', intermsource, count = 1)
                    newsItem['apiSource'] = 'echonest'
                    newsList.append(newsItem)
        elif artistJson['response']['status']['code'] == 5:
            newsList = []
        elif artistJson['response']['status']['code'] != 0:
            raise Exception, "Echonest response code is not 0. It is " + str(artistJson['response']['status']['code']) + ' from this url: ' + url
        else:
            newsList = []
        artistEntry['data'] = newsList
        self.allArtistDataList.append(artistEntry)
        datastoreNewsEntry = models.EchonestNews(key_name = artistEntry['datastore key'], artist_name = artistEntry['artist name'], news_list = json.dumps(newsList))
        datastoreNewsEntry.put()
        memcache.set('echonestNewsCache' + artistEntry['artist name'], newsList, 10800)



class Echonest_Bio_Loader(Echonest_Data_Loader):
    """ This method is a subclass of Echonest_Data_Loader that is specialized for artist biographies."""
    def __init__(self, artistList, deadline = 10, maxFails = 20):
        Echonest_Data_Loader.__init__(self, artistList, deadline, maxFails)
        self.memcacheKey = 'echonestBiographyCache'
        self.echonestDataType = 'bios'
        self.searchBase = 'http://developer.echonest.com/api/v4/artist/biographies?api_key=' + self.apiKey + '&'
        self.searchArgs = {'format' : 'json',}
        self.urlWrapper = self.searchBase + str(urllib.urlencode(self.searchArgs))

    def artistDataFromDatastore(self):
        datastoreEntries = models.EchonestBio.get_by_key_name(self.datastoreKeys)
        for index, artistEntry in enumerate(self.datastoreLookups):
            datastoreEntry = datastoreEntries[index]
            if datastoreEntry is None:
                artistEntry['url'] = self.urlFromName(artistEntry['artist name'])
                self.appendRPC(artistEntry)
            else:
                artistEntry['data'] = json.loads(datastoreEntry.bio_dictionary)
                self.allArtistDataList.append(artistEntry)

    def parseJson(self, artistJson, artistEntry):
        bioData = {}
        if artistJson['response'].has_key('total'):
            if not artistJson['response']['total'] == 0 and artistJson['response']['status']['code'] == 0:
                for entry in artistJson['response']['biographies']:
                    if entry['site'] == 'wikipedia' or entry['site'] == 'Wikipedia':
                        bioData['wikipedia'] = entry
                        bioData['wikipedia']['generalBio'] = re.sub(r'(Early life)(.*)$|(Life and career)(.*)$|(History)(.*)$|(Band history)(.*)$', '', bioData['wikipedia']['text'])
                        if len(bioData['wikipedia']['generalBio']) < 100:
                            bioData['wikipedia']['generalBio'] = bioData['wikipedia']['text'][:600] + '...'
                        elif len(bioData['wikipedia']['generalBio']) > 600:
                            bioData['wikipedia']['generalBio'] = bioData['wikipedia']['generalBio'][:600] + '...'
                        else:
                            bioData['wikipedia']['generalBio'] += '...'
                    if entry['site'] == 'last.fm' or entry['site'] == 'Last.fm':
                        bioData['last.fm'] = entry
                    if bioData.has_key('last.fm') and bioData.has_key('wikipedia'):
                        break
        elif artistJson['response']['status']['code'] == 5:
            bioData = {}
        elif artistJson['response']['status']['code'] != 0:
            raise Exception, "Echonest response code is not 0. It is " + str(artistJson['response']['status']['code']) + ' from this url: ' + url
        else:
            bioData = {}
        artistEntry['data'] = bioData
        self.allArtistDataList.append(artistEntry)
        datastoreBioEntry = models.EchonestBio(key_name = artistEntry['datastore key'], artist_name = artistEntry['artist name'], bio_dictionary = json.dumps(bioData))
        datastoreBioEntry.put()
        memcache.set('echonestBiographyCache' + artistEntry['artist name'], bioData, 604800)



def CorrectArtistName(artist, deadline = 10, maxFails = 20):
    """ This method takes an artist name, a maximum amount of time to wait for a response from echonest in seconds,
        and a maximum amount of url failures as inputs and returns the corrected name if it is found, and None if
        its not."""
    artistList = [artist]
    return CorrectArtistNames(artistList, deadline, maxFails)[0]



def CorrectArtistNames(artists, deadline = 10, maxFails = 20):
    """ This method does the same thing as CorrectArtistName, but recieves an array of artists as
        an input, and returns an array with all the corrected names in the same order."""
    correctedArtistDataLoader = Echonest_Correction_Loader(artists, deadline, maxFails)
    correctedArtistData = correctedArtistDataLoader.load()
    return correctedArtistData



def GetSimilarArtist(artist, deadline = 10, maxFails = 20, maxSimilar = 100):
    """ This method takes an artist name, a maximum amount of time to wait for a response from echonest in seconds,
        a maximum amount of url failures, and a maximum number of similar artists as inputs and returns an array of
        similar artists if it is found, or an empty array if not."""
    artistList = [artist]
    return GetSimilarArtists(artistList, deadline, maxFails, maxSimilar)[0]



def GetSimilarArtists(artists, deadline = 10, maxFails = 20, maxSimilar = 100):
    """ This method does the same thing as GetSimilarArtist, but recieves an array of artists as
        an input, and returns an array with all the similar artist arrays in the same order."""
    similarArtistDataLoader = Echonest_Similar_Artist_Loader(artists, deadline, maxFails, maxSimilar)
    similarArtistData = similarArtistDataLoader.load()
    return similarArtistData



def GetNewsForArtist(artist, deadline = 10, maxFails = 20):
    """ This method takes an artist name, a maximum amount of time to wait for a response from echonest in seconds,
        and a maximum amount of url failures as inputs and returns a news dictionary if it is found, and an empty
        dictionary if its not."""
    artistList = [artist]
    return GetNewsForArtists(artistList, deadline, maxFails)[0]



def GetNewsForArtists(artists, deadline = 10, maxFails = 20):
    """ This method does the same thing as GetNewsForArtist, but recieves an array of artists as
        an input, and returns an array with all the news dictionaries in the same order."""
    newsDataLoader = Echonest_News_Loader(artists, deadline, maxFails)
    newsData = newsDataLoader.load()
    return newsData



def GetBioForArtist(artist, deadline = 10, maxFails = 20):
    """ This method takes an artist name, a maximum amount of time to wait for a response from echonest in seconds,
        and a maximum amount of url failures as inputs and returns a bio dictionary if it is found, and an empty
        dictionary if its not."""
    artistList = [artist]
    return GetBioForArtists(artistList, deadline, maxFails)[0]



def GetBioForArtists(artists, deadline = 10, maxFails = 20):
    """ This method does the same thing as GetBioForArtist, but recieves an array of artists as
        an input, and returns an array with all the bio dictionaries in the same order."""
    bioDataLoader = Echonest_Bio_Loader(artists, deadline, maxFails)
    bioData = bioDataLoader.load()
    return bioData
