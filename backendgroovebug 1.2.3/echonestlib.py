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
from django.utils import simplejson as json
import DataModels as models
from operator import itemgetter, attrgetter
import urllib2, urllib, datetime, re, htmlentitydefs, logging, unicodedata, datetime, time, itertools
logging.getLogger().setLevel(logging.DEBUG)



""" This class is responsible for getting various data from echonest.
    NOTE:
    -takes an artist list and a 'function' argument
    -function can either be 'correct' 'similar' or 'news'"""
class GetEchonestData():
    def __init__(self, function, artistList):
## initialize variables that will be used by all echonest 'functions'
        self.artistList = artistList
        self.failCounter = 1
        self.rpcs = []

## execute code for 'correct' function
        if function == 'correct':
## log the start of the method to google app engine error console
            logging.info('Start getting corrections for ' + str(len(self.artistList)) + ' artists')

## set up wrapper url for echonest API calls
            self.searchBase = 'http://developer.echonest.com/api/v4/artist/search?api_key=269A92REW5YH3KNZW&'
            self.searchArgs = {'format' : 'json',
                               'results' : '1',
                               'fuzzy_match' : 'false',}

## initialize variable to store corrected artist names
            self.correctedArtistList = []

## loop through artist list, checking memcache, then datastore for artist corrections.
## append an rpc if no artist correction is found
            for postIndex, artist in enumerate(self.artistList):
                correctedEntry = {}
                correctedEntry['index'] = postIndex
                correctedEntry['uncorrected name'] = artist

                if artist != ''.encode('utf-8'):
                    cachedCorrectedName = memcache.get('artistVerifyCache' + artist)
                    if cachedCorrectedName is None:
                        try:
                            datastoreCorrectedName = models.ArtistCorrection.get_by_key_name(artist)
                        except Exception:
                            logging.info('This artist messed up: \"' + artist + '\" type is ' + artist.__class__.__name__)
                            datastoreCorrectedName = models.ArtistCorrection.get_by_key_name("there is nobody with this name")
                            
                        if datastoreCorrectedName is None:
                            correctedEntry['url'] = self.searchBase + str(urllib.urlencode(self.searchArgs)) + '&name=' + urllib.quote_plus(artist.encode('utf-8'))
                            self.AppendCorrectedRPC(correctedEntry)
                        else:
                            correctedEntry['corrected name'] = datastoreCorrectedName.corrected_name
                            self.correctedArtistList.append(correctedEntry)
                    else:
                        correctedEntry['corrected name'] = cachedCorrectedName
                        self.correctedArtistList.append(correctedEntry)
                else:
                    correctedEntry['corrected name'] = None
                    self.correctedArtistList.append(correctedEntry)

## loop through rpcs, making an API call for each rpc.
## wait for rpcs every 25 API callsa
            currentRPCs = []
            for index, rpc in enumerate(self.rpcs):
                logging.info('Launching ' + rpc['url'])
                urlfetch.make_fetch_call(rpc['rpc'], rpc['url'])
                currentRPCs.append(rpc['rpc'])
                if index == (len(self.rpcs) - 1) or (len(currentRPCs)%3 == 0):
                    for rpc in currentRPCs:
                        rpc.wait()
                    logging.info('Finished processing ' + str(len(currentRPCs)) + ' rpcs')
                    currentRPCs = []

## sort list of corrected artist names by index of the original artist list
## save final list of corrected artists self.correctedArtistListFinal
            self.correctedArtistListFinal = []
            correctedArtistList = sorted(self.correctedArtistList, key = lambda artist: artist['index'])
            for entry in correctedArtistList:
                name = entry['corrected name']
                if name != 'echonest has no correction for this artist':
                    self.correctedArtistListFinal.append(entry['corrected name'])
                else:
                    self.correctedArtistListFinal.append(None)

## log the end of the method to google app engine error console
            logging.info('Finished getting corrections for ' + str(len(self.artistList)) + ' artists')
            
## execute code for 'similar' function
        elif function == 'similar':
## log the end of the method to google app engine error console
            logging.info('Start getting similar artists for ' + str(len(self.artistList)) + ' artists')

## set up wrapper url for echonest API calls            
            self.searchBase = 'http://developer.echonest.com/api/v4/artist/similar?api_key=269A92REW5YH3KNZW&'
            self.searchArgs = {'format' : 'json',
                               'results' : '100',}
            self.allSimilarList = []
            
            for postIndex, artist in enumerate(self.artistList):
                similarEntry = {}
                similarEntry['index'] = postIndex
                similarEntry['artist name'] = artist

                cachedArtistList = memcache.get('similarArtistCache' + artist)
                if cachedArtistList is None:
                    datastoreArtistList = models.SimilarArtists.get_by_key_name(artist)
                    if datastoreArtistList is None:
                        similarEntry['url'] = str(self.searchBase) + str(urllib.urlencode(self.searchArgs)) + '&name=' + urllib.quote_plus(artist.encode('utf-8'))
                        self.AppendSimilarRPC(similarEntry)
                    else:
                        similarEntry['list'] = datastoreArtistList.similar_artists
                        self.allSimilarList.append(similarEntry)
                else:
                    similarEntry['list'] = cachedArtistList
                    self.allSimilarList.append(similarEntry)

            currentRPCs = []
            for index, rpc in enumerate(self.rpcs):
                logging.info('Launching ' + rpc['url'])
                urlfetch.make_fetch_call(rpc['rpc'], rpc['url'])
                currentRPCs.append(rpc['rpc'])
                if index == (len(self.rpcs) - 1) or (len(currentRPCs)%3 == 0):
                    for rpc in currentRPCs:
                        rpc.wait()
                    logging.info('Finished processing ' + str(len(currentRPCs)) + ' rpcs')
                    currentRPCs = []

            self.similarListFinal = []
            allSimilarList = sorted(self.allSimilarList, key = lambda artist: artist['index'])
            for entry in allSimilarList:
                artistList = entry['list']
                if artistList != []:
                    self.similarListFinal.append(entry['list'])
                else:
                    self.similarListFinal.append([])
            logging.info('Finished getting similar artists for ' + str(len(self.artistList)) + ' artists')

## method that appends a 'remote process call' to the list of rpcs for the 'correct' function
    def AppendCorrectedRPC(self, correctedEntry):
        rpc = urlfetch.create_rpc(deadline = 10)
        rpc.callback = self.CorrectedArtistAsyncCallback(correctedEntry, rpc)
        rpcPair = {}
        rpcPair['rpc'] = rpc
        rpcPair['url'] = correctedEntry['url']
        self.rpcs.append(rpcPair)

  
    def CorrectedArtistAsyncCallback(self, correctedEntry, rpc):
        return lambda: self.HandleCorrectedArtistAsyncCallback(correctedEntry, rpc)

    def HandleCorrectedArtistAsyncCallback(self, correctedEntry, rpc):
        try:
            result = rpc.get_result()
            if result.status_code == 200:
                artistJson = json.loads(result.content)
                if artistJson['response'].has_key('artists') and artistJson['response']['artists'] != [] and artistJson['response']['status']['code'] == 0:
                    correctedName = artistJson['response']['artists'][0]['name']
                elif artistJson['response']['status']['code'] != 0:
                    raise Exception, "Echonest response code is not 0. It is " + str(artistJson['response']['status']['code'])
                else:
                    correctedName = 'echonest has no correction for this artist'
                correctedEntry['corrected name'] = correctedName
                self.correctedArtistList.append(correctedEntry)
                artistCorrectionEntry = models.ArtistCorrection(key_name = correctedEntry['uncorrected name'], uncorrected_name = correctedEntry['uncorrected name'], corrected_name = correctedName)
                artistCorrectionEntry.put()
                memcache.set('artistVerifyCache' + correctedEntry['uncorrected name'], correctedName, 604800)
            else:
                self.failCounter += 1
                if self.failCounter <= 20:
                    time.sleep(.1)
                    logging.info(str(result.status_code) + ' code on url: ' + str(correctedEntry['url']) + '. Re-appending')
                    self.AppendCorrectedRPC(correctedEntry)
                else:
                    raise Exception, "There were " + str(self.failCounter) + ' failed echonest calls, FAILURE'
        except urlfetch.DeadlineExceededError:
            self.failCounter += 1
            if self.failCounter <= 20:
                time.sleep(.1)
                logging.info('urlfetch deadline exceeded error on url: ' + str(correctedEntry['url']) + '. Re-appending')
                self.AppendCorrectedRPC(correctedEntry)
            else:
                raise Exception, "There were " + str(self.failCounter) + ' failed echonest calls, FAILURE'

## method that appends a 'remote process call' to the list of rpcs for the 'similar' function
    def AppendSimilarRPC(self, similarEntry):
        rpc = urlfetch.create_rpc(deadline = 10)
        rpc.callback = self.SimilarArtistAsyncCallback(similarEntry, rpc)
        rpcPair = {}
        rpcPair['rpc'] = rpc
        rpcPair['url'] = similarEntry['url']
        self.rpcs.append(rpcPair)

    def SimilarArtistAsyncCallback(self, similarEntry, rpc):
        return lambda: self.HandleSimilarArtistAsyncCallback(similarEntry, rpc)


    def HandleSimilarArtistAsyncCallback(self, similarEntry, rpc):
        try:
            result = rpc.get_result()
            similarArtistList = []
            if result.status_code == 200:
                artistJson = json.loads(result.content)
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
                similarEntry['list'] = similarArtistList
                self.allSimilarList.append(similarEntry)
                similarArtistEntry = models.SimilarArtists(key_name = similarEntry['artist name'], artist_name = similarEntry['artist name'], similar_artists = similarArtistList)
                similarArtistEntry.put()
                memcache.set('similarArtistCache' + similarEntry['artist name'], similarArtistList, 604800)
            else:
                self.failCounter += 1
                if self.failCounter <= 20:
                    time.sleep(.1)
                    logging.info(str(result.status_code) + ' code on url: ' + str(similarEntry['url']) + '. Re-appending')
                    self.AppendSimilarRPC(similarEntry)
                else:
                    raise Exception, "There were " + str(self.failCounter) + ' failed echonest calls, FAILURE'
        except urlfetch.DeadlineExceededError:
            self.failCounter += 1
            if self.failCounter <= 20:
                time.sleep(.1)
                logging.info('urlfetch deadline exceeded error on url: ' + str(similarEntry['url']) + '. Re-appending')
                self.AppendSimilarRPC(similarEntry)
            else:
                raise Exception, "There were " + str(self.failCounter) + ' failed echonest calls, FAILURE'
""" --- """


    
""" This function checks the memcache, then the datastore for a stored correction for an artist name, returns it
    if it is found, or makes a call to echonest to retrieve the data.
    NOTE:
    -returns 'echonest has no correction for this artist' for corrected artist name if not found
    -raises an exception if the call to the echonest server fails after 4 successive tries"""
def CorrectArtistName(artist):
    artistList = [artist]
    return CorrectArtistNames(artistList)[0]
""" --- """



""" This function does the same thing ass CorrectArtistName, but recieves an array of artists as
    an input, and returns an array with all the corrected names in the same order with names not
    found in echonest inserted in place of said names."""
def CorrectArtistNames(artists):
    correctedArtistData = GetEchonestData('correct', artists)   
    return correctedArtistData.correctedArtistListFinal
""" --- """


    
""" This function checks the memcache, then the datastore for a stored similar artist list for an artist name, returns it
    if it is found, or makes a call to echonest to retrieve the data.
    NOTE:
    -returns 'echonest has no correction for this artist' for corrected artist name if not found
    -raises an exception if the call to the echonest server fails after 4 successive tries"""
def GetSimilarArtist(artist):
    artistList = [artist]
    return GetSimilarArtists(artistList)[0]
""" --- """



""" This function does the same thing ass GetSimilarArtist, but recieves an array of artists as
    an input, and returns an array of arrays containing similar artists and an empty array if no
    similar artists are found for an artist"""
def GetSimilarArtists(artists):
    similarArtistData = GetEchonestData('similar', artists)   
    return similarArtistData.similarListFinal
""" --- """
