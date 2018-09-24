# -*- coding: utf-8 -*-
""" This file contains methods, and the database models which are used throughout the app"""
## test facebook app info
##FACEBOOK_APP_ID = "165771780180103"
##FACEBOOK_APP_SECRET = "f13b46bb31096fb5e1eebe3ff3c328a2"
## groovebug facebook app info
FACEBOOK_APP_ID = "120878094678054"
FACEBOOK_APP_SECRET = "3537e2de75869e44ebe27bde09836c25"

import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import db, deferred
from google.appengine.api import urlfetch, memcache
from google.appengine.runtime import DeadlineExceededError
from django.utils import simplejson as json
import echonestlib as echonest
from operator import itemgetter, attrgetter
import urllib2, urllib, datetime, re, htmlentitydefs, logging, unicodedata, math, facebook
logging.getLogger().setLevel(logging.DEBUG)




""" This section of code which ends with a "---" defines the classes
    extending db.Model which will be used to store data in the datastore"""



""" This class defines the database model that will store facebook user entities"""
class FacebookUser(db.Model):
    updated = db.DateTimeProperty(auto_now=True)
    groovebug_UDID = db.StringProperty()
    name = db.StringProperty()
    profile_url = db.StringProperty()
    access_token = db.StringProperty(required=True)
    fbArtistList = db.StringListProperty(default = None)
    fbArtistListString = db.TextProperty(default = None)
    friendsJsonData = db.TextProperty(default = None)
    friendsData = db.TextProperty(default = None)
    friendsString = db.TextProperty(default = None)
""" --- """



""" This class defines the database model that stores corrected artist entries"""
class ArtistCorrection(db.Model):
    uncorrected_name = db.StringProperty(required=True)
    corrected_name = db.StringProperty(required=True)
    date_added = db.DateTimeProperty(auto_now=True)
""" --- """



""" This class defines the database model that stores similar artist entries"""
class SimilarArtists(db.Model):
    artist_name = db.StringProperty(required=True)
    similar_artists = db.TextProperty(default = None)
    date_added = db.DateTimeProperty(auto_now=True)
""" --- """


""" This class defines the database model that stores similar artist entries"""
class EchonestNews(db.Model):
    artist_name = db.StringProperty(required=True)
    news_list = db.TextProperty(default = None)
    date_added = db.DateTimeProperty(auto_now=True)
""" --- """



""" This class defines the database model that stores similar artist entries"""
class EchonestBio(db.Model):
    artist_name = db.StringProperty(required=True)
    bio_dictionary = db.TextProperty(default = None)
    date_added = db.DateTimeProperty(auto_now=True)
""" --- """



""" This class defines the database model that will store artist backend user entities"""
class ArtistBackendUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    musicLikes = db.TextProperty(default = None)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    fbArtistList = db.StringListProperty(default = None)
    fbArtistListString = db.TextProperty(default = None)
""" --- """


""" This class defines the database model that will store user entities"""
class GroovebugUser(db.Model):
    userId = db.StringProperty()
    artistList = db.StringListProperty(default = None)
    artistListJson = db.TextProperty(default = None)
    groovebugFavorites = db.StringListProperty(default = None)
    facebookFavorites = db.StringListProperty(default = None)
    facebookFavoritesJson = db.TextProperty(default = None)
    groovebugFavoritesJson = db.TextProperty(default = None)
    facebookFriendsData = db.TextProperty(default = None)
    verifiedJson = db.TextProperty()
    visitedSites = db.TextProperty(default = '')
""" --- """



"""This class defines the database model that will store composite page entities"""
class CompositePage(db.Model):
    title = db.StringProperty()
    compositeType = db.StringProperty(default = 'Artists')
    status = db.StringProperty(default = 'Normal')
    artistList = db.StringListProperty(default = None)
    content = db.StringProperty(default = 'N/A')
    contentType = db.StringProperty(default = '-Select-')
    summary = db.TextProperty()
    summaryUrl = db.StringProperty(default = 'N/A')
    graphicBlobKey = db.StringProperty(default='N/A')
    graphicUrl = db.StringProperty(default = 'N/A')
    compositeUrl = db.StringProperty()
    thumbnail = db.BlobProperty()
    thumbnailBlobKey = db.StringProperty(default='N/A')
    thumbnailUrl = db.StringProperty(default = 'N/A')
    artistListJson = db.TextProperty()
""" --- """


class JsonProperty(db.TextProperty):
    def validate(self, value):
	return value
	 
    def get_value_for_datastore(self, model_instance):
	result = super(JsonProperty, self).get_value_for_datastore(model_instance)
	result = json.dumps(result)
	return db.Text(result)
	 
    def make_value_from_datastore(self, value):
	try:
	    value = json.loads(str(value))
	except:
	    pass
	 
	return super(JsonProperty, self).make_value_from_datastore(value)



""" Section ending with "---" defines class that models the Artist Image datastore"""
class ArtistImages(db.Model):
    artistName = db.StringProperty(required=True)
    artistEchoId = db.StringProperty()
    dateAdded = db.DateProperty()
    artistImgNum = db.IntegerProperty()
    artistOrigImgUrl = db.StringProperty()
    artistImg = db.BlobProperty(default=None)
    artistImgWidth = db.IntegerProperty()
    artistImgHeight = db.IntegerProperty()
    artistImgBlobKey = db.StringProperty()
    artistImgUrl = db.StringProperty()
    artistImgLicense = JsonProperty()
    artistReducedImg = db.BlobProperty(default=None)
    artistReducedImgWidth = db.IntegerProperty()
    artistReducedImgHeight = db.IntegerProperty()
    artistReducedImgBlobKey = db.StringProperty()
    artistReducedImgUrl  = db.StringProperty()
    artistThmb = db.BlobProperty(default=None)
    artistThmbBlobKey = db.StringProperty()
    artistThmbUrl = db.StringProperty()

""" --- """



""" Section ending with "---" defines class that models the Artist Bios datastore"""
class ArtistBios(db.Model):
    artistName = db.StringProperty(required=True)
    artistBio = db.TextProperty()
    artistURL = db.StringProperty()

""" --- """



""" Section ending with "---" defines class that models the Artist video promote and exclude list datastore"""
class ArtistVideos(db.Model):
    artistName = db.StringProperty(required=True)
    videosToPromote = JsonProperty()
    videosToExclude = db.StringListProperty()

""" --- """



""" Section ending with "---" defines class that models the Artist audio list datastore"""
class PromotedAudio(db.Model):
    artistName = db.StringProperty(required=True)
    title = db.StringProperty()
    trackNum = db.IntegerProperty()
    album = db.StringProperty()
    buyUrl = db.StringProperty()
    blobKey = db.StringProperty()
    url = db.StringProperty()
    imgBlobkey = db.StringProperty()
    imgUrl = db.StringProperty()
    thumbBlobkey = db.StringProperty()
    thumbUrl = db.StringProperty()
    PromotedToList = db.StringListProperty()
    artistListErrors = db.StringListProperty()
    #artistTracks = JsonProperty()
""" --- """



""" Section ending with "---" defines class that models the Artist drawer datastore for promoting audio and video"""
class ArtistDrawer(db.Model):
    artistName = db.StringProperty(required=True)
    promotedTitle = db.StringProperty()
    promotedArtist = db.StringProperty()
    audioToPromote = db.ReferenceProperty(PromotedAudio, collection_name='promoted_to_artists')
    #audioToPromote = db.StringProperty()
    videoToPromote = db.StringProperty()
    #videoToPromote = db.ReferenceProperty(PromotedVideo)

""" --- """



""" Section ending with "---" defines class that models the Artist audio list datastore"""
class PromotedNews(db.Model):
    artistName = db.StringProperty(required=True)
    title = db.StringProperty()
    summary = db.TextProperty()
    url = db.StringProperty()
    date = db.StringProperty()
    publisher = db.StringProperty()
    feed_link = db.StringProperty()
    articleSource = db.StringProperty()
    apiSource = db.StringProperty()

""" --- """

""" Section ending with "---" defines class that models the Artist audio list datastore"""
class ArtistSocial(db.Model):
    artistName = db.StringProperty(required=True)
    twitter = db.StringProperty()
    facebook = db.StringProperty()
    tumbler = db.StringProperty()
    myspace = db.StringProperty()

""" --- """
""" ---------------------------------------------------------------------------------------------------------------------- """







###############################################################################################################################
""" This section of code defines functions that are used throughout the application"""
###############################################################################################################################
""" This section of code which ends with a "---" defines the function that recieves
    a url as an input, and tries to load a json document up to 'maxTries' times.
    returns an empty list if all tries fail."""
def RetryLoadJson(url, counter = 0, maxTries = 3):
    try:
        try:
            result = urlfetch.fetch(url, deadline=10)
            loadedJson = json.loads(result.content)
        except urlfetch.DownloadError:
            if counter < maxTries:
                counter += 1
                return RetryLoadJson(url, counter)
            else:
                return []
    except DeadlineExceededError:
        errorMessage = 'App Engine reached 30 second deadline while trying to fetch this url: ' + url
        raise Exception, errorMessage
    return loadedJson
""" --- """



""" Duplicate of RetryLoadJson for similar artists"""
def RetryLoadSimilarJson(url, counter = 0, maxTries = 3):
    try:
        try:
            result = urlfetch.fetch(url)
            loadedJson = json.loads(result.content)
        except urlfetch.DownloadError:
            if counter < maxTries:
                counter += 1
                return RetryLoadJson(url, counter)
            else:
                return []
    except DeadlineExceededError:
        errorMessage = 'App Engine reached 30 second deadline while trying to fetch this url: ' + url
        raise Exception, errorMessage
    return loadedJson
""" --- """



def natural(key):
    """natural(key)
    usage:
    >>> sorted(unsorted, key=natural)
    >>> unsorted.sort(key=natural)

    if key is unicode, it simplifies key to ascii using unicodedata.normalize.
    """

    if isinstance(key, basestring):
        if isinstance(key, unicode):
            key = unicodedata.normalize('NFKD', key.lower()).encode('ascii', 'ignore')
        else:
            key = key.lower()
        key = re.sub('(^The )|(^the )|(^A )|(^a )', '', key)
        return [int(n) if n else s for n,s in re.findall(r'(\d+)|(\D+)', key)]
    else:
        key = re.sub('(^The )|(^the )|(^A )|(^a )', '', key)
        return key



""" This function removes HTML or XML character references and entities from a text
    string and returns the plain text, as a Unicode string, if necessary.
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



""" This function checks to see if an thumbnail exists for the artist requested"""
def getThumb(artistName):

    result = db.GqlQuery("SELECT * FROM ArtistImages WHERE artistName = :1 LIMIT 1",
      artistName).fetch(1)

    if (len(result) > 0):
        return result[0].artistThmbUrl
    else:
        return None
""" --- """



""" This function checks to see if an thumbnail exists for the artist requested"""
def getBio(artist):
    artistName = urllib.quote_plus(artist.encode('utf-8'))
    result = db.GqlQuery("SELECT * FROM ArtistBios WHERE artistName = :1 LIMIT 1",
      artistName).fetch(1)

    if (len(result) > 0):
        return result[0]
    else:
        return None
""" --- """



""" This function checks to see if the encoding of a string requires latin-1 """
def ChkTxtEnc(InTxt):
    UseUTF8 = False
    UseLatin = False
    for i in InTxt:
        if ord(i) > 255:
            UseUTF8 = True
        elif ord(i) > 127:
            UseLatin = True
                        
    if UseUTF8:
        OutTxt = InTxt.encode('utf-8')
    elif UseLatin:
        OutTxt = InTxt.encode('latin-1')
    else:
        OutTxt = InTxt

    TestTxt = ''
    for i in OutTxt:
        if ord(i) in [225, 227, 229, 232, 233, 237, 243, 246, 252]:
            OutTxt = InTxt
            break
        #TestTxt = TestTxt + str(i) + '(' + str(ord(i)) + ')'
                
    return OutTxt

""" --- """



""" This function recieves user library data from an HTML POST and a list of
    corrected artists names that correspond to the data and maps corrected artist names
    to entries in the user library to their appropriate artist list."""
def MapArtists(userArtists, correctedArtistNames):
    libraryMappings = {}
    favoritesMappings = {}
    for index, artist in enumerate(userArtists):
        name = artist['name']
        correctedName = correctedArtistNames[index]
        if correctedName != None:
            if artist.has_key('lists'):
                if 'library' in artist['lists']:
                    if not libraryMappings.has_key(correctedName):
                        libraryMappings[correctedName] = [name]
                    else:
                        if not name in libraryMappings[correctedName]:
                            libraryMappings[correctedName].append(name)
                if 'favorites' in artist['lists']:
                    if not favoritesMappings.has_key(correctedName):
                        favoritesMappings[correctedName] = [name]
                    else:
                        if not name in favoritesMappings[correctedName]:
                            favoritesMappings[correctedName].append(name)
            else:
                if not libraryMappings.has_key(correctedName):
                    libraryMappings[correctedName] = [name]
                else:
                    if not name in libraryMappings[correctedName]:
                        libraryMappings[correctedName].append(name)
            
    return libraryMappings, favoritesMappings
""" --- """



""" This function does the calculations for libary matching to corresponding composite page """
def CompositeScoreCallback(rpc, gSimArtArr, artistList):
    return lambda: HandleCompositeScoreCallbackResult(rpc, gSimArtArr, artistList)
""" --- """



""" This function does the calculations for libary matching to corresponding composite page"""
def HandleCompositeScoreCallbackResult(rpc, gSimArtArr, artistList):
    result = rpc.get_result()
    if result.status_code == 200:
        simArt = json.loads(result.content)
        if simArt != []:
            if simArt['response']['status']['code'] == 0:
                for sEntry in simArt['response']['artists']:
                    if sEntry['name'] not in artistList:
                        if sEntry['name'] not in gSimArtArr:
                            gSimArtArr.append(sEntry['name'])
                        else:
                            pass
                    else:
                        pass
""" --- """



#############################################################################################################################################
""" -------------------------------------------------ArtistVerificationHandler.py-------------------------------------------------------- """
""" This function recieves a user id and a json document with artist names to be
    verified, and returns the json document of verified artists. The calls to
    echonest to verify the artist name are also cached"""
def GetVerifiedArtist(userData, user, index = 0, fbID = None, fbAuth = None):
## Load current user from the datastore and create dictionary that will be returned at the end of the function
    currentUser = GroovebugUser.get_by_key_name(user)
    finalPreJson = {}
    finalPreJson['old'] = userData
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'user' : str(user)}
    finalPreJson['library mappings'] = {}
    finalPreJson['favorites mappings'] = {}
## Log the total number of artists in the users library to the google app engine dashboard
    logging.info('number of artists: ' + str(len(userData['artists'])))

## Parse user artist list, use echonest library to correct names, and map the artist names to corrected names in appropriate list.
    recievedArtistlist = []
    if userData.has_key('artists'):
        for artist in userData['artists']:
            recievedArtistlist.append(artist['name'])
        correctedArtistList = echonest.CorrectArtistNames(recievedArtistlist)
    libraryMappings, favoritesMappings = MapArtists(userData['artists'], correctedArtistList)
    finalPreJson['corrected'] = correctedArtistList
    finalPreJson['library mappings'] = libraryMappings
    finalPreJson['favorites mappings'] = favoritesMappings

## Create library list from user library, sort them alphabetically, and create a new list with corresponding magazine links    
    artistList = libraryMappings.keys()
    artistList = sorted(artistList, key = lambda artist: natural(artist))

## Create favorites list from user library, sort them alphabetically, and create a new list with corresponding magazine links    
    groovebugFavorites = favoritesMappings.keys()  
    groovebugFavorites = sorted(groovebugFavorites, key = lambda artist: natural(artist))

## If there is a facebook ID and authentication token in the call to the verify handler,
## retrieve facebook music likes
    if fbID != None and fbAuth != None:
        facebookFavorites = []
        fbuser = FacebookUser.get_by_key_name(fbID)
        if not fbuser:
            graph = facebook.GraphAPI(fbAuth)
            profile = graph.get_object("me")
            musicLikes = graph.get_connections(profile["id"], "music")
            fbArtistList = []
            if musicLikes['data'] != []:
                for artist in musicLikes['data']:
                    if artist['category'] == "Musician/band":
                        fbArtistList.append(artist['name'])
            correctedFacebookFavorites = echonest.CorrectArtistNames(fbArtistList)
            facebookFavorites = []
            for artist in correctedFacebookFavorites:
                if artist != None:
                    facebookFavorites.append(artist)
            facebookFavorites = sorted(facebookFavorites, key = lambda artist: natural(artist))
                        
            fbuser = FacebookUser(key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name = profile["name"],
                        profile_url = profile["link"],
                        access_token = (fbAuth))
            fbuser.musicLikes = json.dumps(musicLikes)
            if facebookFavorites != []:
                fbuser.fbArtistList = facebookFavorites
            fbuser.put()
        if fbuser:
            facebookFavorites = fbuser.fbArtistList
            if currentUser is not None:
                currentUser.facebookFavorites = facebookFavorites
            finalPreJson['facebook list'] = facebookFavorites

    if currentUser is None:
        currentUser = GroovebugUser(key_name = user, userId = user, groovebugFavorites = groovebugFavorites, artistList = artistList)
        currentUser.put()
    else:
        currentUser.groovebugFavorites = groovebugFavorites
        currentUser.artistList = artistList
        currentUser.put()

    return finalPreJson
""" --- """



#############################################################################################################################################
""" -------------------------------------------------BioHandler.py-------------------------------------------------------- """
""" This method recieves an artist name as an input and outputs data that will be
    used in the bio html output. There is an optional second argument for the max
    retries for loading a json document"""
def GetArtistBio(artist, maxLookupRetry = 10):
## Encode results into unicode which can be parsed by API
##    artist = artist.encode('utf-8')
    groovebugContent = False
    
    if artist == 'AM & Shawn Lee':
        groovebugContent = True

    gbBio = getBio(artist)
    if gbBio:
        groovebugContent = True
    
## Initialize dictionary that will hold bio data
    artistBio = {}
    artistBio['status'] = {'error' : '0', 'version' : '1.0'}
    artistBio['bios'] = {}

    if groovebugContent == True:
        if artist == 'AM & Shawn Lee':
            bio = {}
            bio['source'] = 'Groovebug'
            bio['text'] = 'Celestial Electric, the first-ever collaboration by AM & Shawn Lee, marks the launch of a timely musical partnership that\'s more than the sum of its already formidable parts.  Although both artists are already well-established for their own work, their audacious new set finds these two sonic iconoclasts joining forces to create music that\'s distinctly adventurous, yet effortlessly accessible and emotionally resonant. The project marks a creative milestone for both artists, offering timeless, deeply compelling music that showcases the duo\'s remarkable creative chemistry.'
            bio['text'] = bio['text'].encode('utf-8')
            bio['url'] = 'http://www.eslmusic.com/artist/am_shawn_lee'
            artistBio['bios']['Groovebug Content'] = bio
        else:
            bio = {}
            bio['source'] = 'Groovebug'
            bio['text'] = gbBio.artistBio
            bio['text'] = bio['text'].encode('utf-8')
            bio['url'] = gbBio.artistURL
            artistBio['bios']['Groovebug Content'] = bio

    else:
        bioData = echonest.GetBioForArtist(artist)
        if bioData == {}:
            artistBio['status']['error'] = 'bio not found'
        else:
            artistBio['bios'] = bioData
    return artistBio
""" --- """



#############################################################################################################################################
""" --------------------------------------------------CompositeHandler.py-------------------------------------------------------- """
""" This section of code which ends with a "---" block defines the function
    that recieves an composite name as an input, and returns a dictionary
    with information about the composite."""
def GetCompositeData(name):
    name = urllib.unquote_plus(name)
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0',
                              'version' : '1.0',}
    
    compositePages = CompositePage.gql("WHERE title = :title", title = name)
    if compositePages is None:
        finalPreJson['status']['error'] = 'Sorry, ' + name + ' doesnt exist in Composite database'
        return finalPreJson
    else:
        for page in compositePages:
            pagekey = page.key()
            pageID = pagekey.id()
            finalPreJson['name'] = page.title
            artistListJson = page.artistListJson
            artistListData = json.loads(artistListJson.encode('utf-8'))
            finalPreJson['artist list'] = artistListData
            if page.contentType == 'userInput':
                finalPreJson['content'] = 'http://' + str(hostUrl) + '/v1/compositehtml?id=' + str(pageID)
            else:
                finalPreJson['content'] = page.content
            finalPreJson['thumbnail'] = page.thumbnailUrl
            finalPreJson['header'] = page.compositeType
            finalPreJson['background'] = 'http://backendgroovebug.appspot.com/v1/backgrounds?artist=blank+images'
            
    return finalPreJson      
""" --- """



def GetFriendsTileScore(friendArtistList, artistList):
    gArtArr = friendArtistList
    if len(gArtArr) != 0:
        simScoreTot = 0
        rpcs = []
        gSimArtArr = []
        sUser = set(artistList)
        simLists = friendArtistList

        sSimArtList = set(simLists)
        sSimArtMatch = sSimArtList & sUser

        if len(simLists) != 0:
            cScore = round((float(len(sSimArtMatch))/float(len(simLists)))*100, 1)
        else:
            cScore = 0
    else:
        cScore = 0
        
    return float(cScore)
#############################################################################################################################################
""" -------------------------------------------------HomeHandler.py-------------------------------------------------------- """
""" This method recieves the users artist list and compares that with a composite tile artist list to calculate a match
percent score"""
def getCompositeScore(composite, artistList):
    #gList = {}
    gArtArr = []
        
    simKey = composite.title + ' Sims'

    gSimArtArr = memcache.get(simKey)
    if gSimArtArr is None:
        gSimArtArr = []
        
    if len(gSimArtArr) > 0:
        for gArtEntry in composite.artistList:
            gArtArr.append(gArtEntry)
    else:
        rpcs = []
        gSimArtArr = []
        for gArtEntry in composite.artistList:
            gArtArr.append(gArtEntry)
            #a = artist.Artist(gArtEntry)
            #simArt = a.get_similar(results=10)
            artist = gArtEntry.encode('utf-8')
            artist = urllib.quote_plus(artist)

            similarBase = 'http://developer.echonest.com/api/v4/artist/similar?'
            apiKey = 'api_key=269A92REW5YH3KNZW&'
            similarArgs = {'format' : 'json',
                           'results' : '10',}
            similarUrl = str(similarBase) + str(apiKey) + str(urllib.urlencode(similarArgs)) + '&name=' + artist
            rpc = urlfetch.create_rpc(deadline = 10)
            rpc.callback = CompositeScoreCallback(rpc, gSimArtArr, composite.artistList)
            urlfetch.make_fetch_call(rpc, similarUrl)
            rpcs.append(rpc)
            
        for rpc in rpcs:
            rpc.wait()
            
        memTest = memcache.get(simKey)
        if memTest is not None:
            if not memcache.set(simKey, gSimArtArr, 604800):
                logging.error("Memcache set failed for " + simKey)
        else:
            if not memcache.add(simKey, gSimArtArr, 604800):
                logging.error("Memcache add failed for " + simKey)

    sUser = set(artistList)
    sArtArr = set(gArtArr)
    sSimArtArr = set(gSimArtArr)
    sArtMatch = sArtArr & sUser
    sSimArtMatch = sSimArtArr & sUser

    if len(gArtArr) != 0 and len(gSimArtArr) != 0:
        artScore = round((float(len(sArtMatch)) * 100)/ float(len(gArtArr)), 2)
        simScore = round((float(len(sSimArtMatch)) * 100)/ float(len(gSimArtArr)), 2)
        cScore = round((artScore + ((100.0 - artScore) * simScore)/100.0), 1)
    else:
        cScore = 0
    return float(cScore)
""" --- """



""" This method recieves the users artist list and compares that with a composite tile artist list to calculate a match
percent score"""
def getCompositeScoreNew(composite, artistList):
    gArtArr = composite.artistList
    if len(gArtArr) != 0:
        simScoreTot = 0
        rpcs = []
        gSimArtArr = []
        sUser = set(artistList)
        
## Search memcache for list of similar artists for given composite tile
## Make call to echonest and store results in memcache if no list is found in cache
        simLists = memcache.get('compositeSimilarListsCache' + composite.title)
        if simLists is None:
            simLists = echonest.GetSimilarArtists(composite.artistList)
            memcache.set('compositeSimilarListsCache' + composite.title, simLists, 604800)
        else:
            logging.info('fetched similar artists for ' + composite.title + ' from memcache')

        for i, lEntry in enumerate(simLists):
            #artist = gArtArr[i].encode('utf-8')
            #artist = urllib.quote_plus(artist)
            
            sSimArtList = set(lEntry)
            sSimArtMatch = sSimArtList & sUser

            if len(lEntry) != 0:
                simScore = math.sqrt(float(len(sSimArtMatch))/float(len(lEntry)))
            else:
                simScore = 0

            simScoreTot = simScoreTot + simScore            

            #simKey = artist + ' SimList'
            #try:
            #    memTest = memcache.get(simKey)
            #    if memTest:
            #        memcache.set(simKey, lEntry, 604800)
            #    else:
            #        memcache.add(simKey, lEntry, 604800)
            #except Exception, error:
            #    logging.error('Memcache Error - ' + error)
                
        cScore = round(float(simScoreTot)*100.0/float(len(gArtArr)), 1)
        
    return float(cScore)
""" --- """


#############################################################################################################################################
""" -------------------------------------------------v2/HomeHandler.py-------------------------------------------------------- """
""" This function recieves a user id and a json document with artist names to be
    verified, and returns the json document of verified artists. The calls to
    echonest to verify the artist name are also cached"""
def GetVerifiedData(userData, user, fbAuth = None):
## Load current user from the datastore and create dictionary that will be returned at the end of the function
    currentUser = GroovebugUser.get_by_key_name(user)
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'user' : str(user)}
    finalPreJson['featured'] = 'http://' + str(hostUrl) + "/v2/featured?user=" + str(user)
## If there is an authentication token in the call to the home handler,
## creat a link to the facebook friends handler
    if fbAuth != None:
        finalPreJson['friends'] = 'http://' + str(hostUrl) + "/v1/fbfriends?user=" + str(user) + '&fbauth=' + fbAuth
    else:
        finalPreJson['friends'] = None
    finalPreJson['mappings'] = {}
    
## Log the total number of artists in the users library to the google app engine dashboard
    logging.info('number of artists: ' + str(len(userData['artists'])))

## Parse user artist list, use echonest library to correct names, and map the artist names to corrected names in appropriate list.
    recievedArtistlist = []
    if userData.has_key('artists'):
        for artist in userData['artists']:
            recievedArtistlist.append(artist['name'])
        correctedArtistList = echonest.CorrectArtistNames(recievedArtistlist)
    libraryMappings, favoritesMappings = MapArtists(userData['artists'], correctedArtistList)
    finalPreJson['corrected'] = correctedArtistList
    finalPreJson['mappings']['library mappings'] = libraryMappings
    finalPreJson['mappings']['favorites mappings'] = favoritesMappings

## Create library list from user library, sort them alphabetically, and create a new list with corresponding magazine links    
    artistList = libraryMappings.keys()
    artistList = sorted(artistList, key = lambda artist: natural(artist))
    artistListData = []
    for artist in artistList:
        artistDictEntry = {}
        artistDictEntry['name'] = artist
        artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
        artistListData.append(artistDictEntry)
    finalPreJson['library'] = artistListData

## Create favorites list from user library, sort them alphabetically, and create a new list with corresponding magazine links    
    groovebugFavorites = favoritesMappings.keys()  
    groovebugFavorites = sorted(groovebugFavorites, key = lambda artist: natural(artist))
    groovebugFavoritesData = []
    for artist in groovebugFavorites:
        artistDictEntry = {}
        artistDictEntry['name'] = artist
        artistDictEntry['magazine'] = 'http://' + str(hostUrl) + "/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
        groovebugFavoritesData.append(artistDictEntry)
    finalPreJson['favorites'] = groovebugFavoritesData

    if currentUser is None:
        currentUser = GroovebugUser(key_name = user, userId = user, groovebugFavorites = groovebugFavorites, artistList = artistList, verifiedJson = json.dumps(finalPreJson).encode('utf-8'))
        currentUser.put()
    else:
        currentUser.groovebugFavorites = groovebugFavorites
        currentUser.artistList = artistList
        currentUser.verifiedJson = json.dumps(finalPreJson).encode('utf-8')
        currentUser.put()

    return finalPreJson
""" --- """


""" This function recieves a user id and a json document with artist names to be
    verified, and returns the json document of verified artists. The calls to
    echonest to verify the artist name are also cached"""
def GetSavedUserData(user, fbAuth = None):
## Load current user from the datastore and create dictionary that will be returned at the end of the function
    currentUser = GroovebugUser.get_by_key_name(user)
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0', 'user' : str(user)}
    finalPreJson['featured'] = 'http://' + str(hostUrl) + "/v2/featured?user=" + str(user)
## If there is an authentication token in the call to the home handler,
## creat a link to the facebook friends handler
    if fbAuth != None:
        finalPreJson['friends'] = 'http://' + str(hostUrl) + "/v1/fbfriends?user=" + str(user) + '&fbauth=' + fbAuth
    else:
        finalPreJson['friends'] = None
    finalPreJson['mappings'] = {}

    if currentUser is not None:
        finalPreJson['library'] = json.loads(currentUser.artistListJson)
        finalPreJson['favorites'] = json.loads(currentUser.groovebugFavoritesJson)
    else:
        finalPreJson['library'] = []
        finalPreJson['favorites'] = []

    return finalPreJson
""" --- """



#############################################################################################################################################
""" -------------------------------------------------MagazineHandler.py-------------------------------------------------------- """
""" This function recieves an artist name as an input and outputs a json formatted list
    of links to our different Handlers and a corrected name dictionary entry.
    There is an optional third argument for the max retries for loading a json document"""
def GetArtistMagazine(artist, user = 'None'):
## Initiallize the dictionary that will eventually be converted to json
    finalPreJson = {}
    finalPreJson['status'] = {'error' : '0', 'version' : '1.0'}
    finalPreJson['name'] = {'entered' : artist, 'corrected' : None}

## Get Json document with artist information using Echonest lookup api
    correctedArtistName = echonest.CorrectArtistName(artist)

## Return blank arrays for everything if artist isnt found    
    if correctedArtistName == None:
        finalPreJson['status']['error'] = 'artist not found in echonest'
        finalJson = json.dumps(finalPreJson, separators=(',',':'))
        return finalJson

## Update corrected name
    else:
        finalPreJson['name']['corrected'] = correctedArtistName
        artist = urllib.quote_plus(correctedArtistName.encode('utf-8'))

## Add URL link for the Biography HTML file to finalPreJson.
    finalPreJson['bio'] = {}
    finalPreJson['bio']['html'] = 'http://' + str(hostUrl) + '/v1/bio?artist=' + artist
    if not user == 'None':
        finalPreJson['bio']['html'] = finalPreJson['bio']['html'] + '&user=' + user

## Add URL link for the Youtube Videos HTML file to finalPreJson.
    finalPreJson['videos'] = {}
    finalPreJson['videos']['html'] = 'http://' + str(hostUrl) + '/v1/videos?artist=' + artist
    if not user == 'None':
        finalPreJson['videos']['html'] = finalPreJson['videos']['html'] + '&user=' + user

## Add URL link for the News HTML file to finalPreJson.
    finalPreJson['news'] = {}
    finalPreJson['news']['html'] = 'http://' + str(hostUrl) + '/v1/news?artist=' + artist
    if not user == 'None':
        finalPreJson['news']['html'] = finalPreJson['news']['html'] + '&user=' + user

## Add URL link for the iTunes music Json file to finalPreJson.
    finalPreJson['music'] = {}
    finalPreJson['music']['json'] = 'http://' + str(hostUrl) + '/v1/music?artist=' + artist
    if not user == 'None':
        finalPreJson['music']['json'] = finalPreJson['music']['json'] + '&user=' + user

## Add URL link for the Similar Artists Json file to finalPreJson.
    finalPreJson['similar'] = {}
    finalPreJson['similar']['json'] = 'http://' + str(hostUrl) + '/v1/similar?artist=' + artist
    if not user == 'None':
        finalPreJson['similar']['json'] = finalPreJson['similar']['json'] + '&user=' + user

## Add URL link for the Background images Json file to finalPreJson.
    finalPreJson['backgrounds'] = {}
    finalPreJson['backgrounds']['json'] = 'http://' + str(hostUrl) + '/v1/backgrounds?artist=' + artist

## Add URL link for the Twitter Json file to finalPreJson.
    finalPreJson['twitter'] = {}
    finalPreJson['twitter']['json'] = 'http://' + str(hostUrl) + '/v1/twitter?artist=' + artist

## Add URL link for the Thumbnail image Json file to finalPreJson.
    finalPreJson['thumbnail'] = {}
    thumbUrl = getThumb(artist)
    if thumbUrl == None:
        finalPreJson['thumbnail']['json'] = 'http://' + str(hostUrl) + '/htmlimages/missing_profile_icon.png'
    else:
        finalPreJson['thumbnail']['json'] = thumbUrl

## Encode final dictionary into json and return it
    finalJson = json.dumps(finalPreJson)
    return finalJson
""" --- """



#############################################################################################################################################
""" -------------CompositeHandler.py-------------------NewsHandler.py-------------------------------------------------------- """
""" This function recieves an artist name as an input and outputs data that will
    be used in the news html output. an optional second parameter, maxResults,
    is available to change the maximum number of results returned. default is 8"""
def GetArtistNews(artist, maxResults = 8, blink=True, edit=False):
# Encode results into unicode which can be parsed by API
    uArtist = artist.encode('utf-8')
    artistName = urllib.quote_plus(uArtist)

# Create blank dictionary that will contain news results and info
# about the search
    artistNews = {}
    artistNews['status'] = {'error' : '0', 'version' : '1.0'}
    artistNews['stories'] = []
    artistFound = False

    promoNews = {}
    promoNews['stories'] = []

    results = db.GqlQuery("SELECT * FROM PromotedNews WHERE artistName = :1 LIMIT 100",
      artistName).fetch(maxResults)

    if (len(results) > 0):
        for entry in results:
            newsItem = {}
            newsItem['key'] = entry.key()
            newsItem['title'] = entry.title
            newsItem['summary'] = entry.summary
            if len(newsItem['summary']) > 350:
                newsItem['summary'] = newsItem['summary'][:350] + '...'
            newsItem['date'] = entry.date
            newsItem['url'] = entry.url
            newsItem['articleSource'] = entry.articleSource
            newsItem['apiSource'] = entry.apiSource
            newsItem['promoted'] = True
            promoNews['stories'].append(newsItem)
            
        sortedArtistNews = sorted(promoNews['stories'], key=itemgetter('date'), reverse=True)
        promoNews['stories'] = sortedArtistNews

    data = memcache.get('artistNews' + artistName)
    if data is not None:
        if data.has_key('stories'):
            if data['stories'] is not None:
                if len(data['stories']) > 0:
                    if not edit and not(len(promoNews['stories']) > 0):
                        return data
                    else:
                        artistNews['stories'] = data['stories']
                        artistFound = True
                else:
                    data = None
            else:
                data = None
        else:
            data = None

       
# Obtain blinkfire news items
    itemCnt = len(promoNews['stories']) + len(artistNews['stories'])
    if blink and  itemCnt < maxResults:
        #searchBase = 'http://music-news.blinkfirelabs.com/news/v1?key=foo&lr=lang_en&max_results=' + str(maxResults) + '&q="' + uArtist + '"'
        searchBase = 'http://music-news.blinkfirelabs.com/news/v1?key=foo&lr=lang_en&max_results=' + str(maxResults) + '&q=' + artistName
        logging.info('url call - ' + str(searchBase))
        try:
            newsJson = json.load(urllib2.urlopen(searchBase))
        except Exception:
            newsJson = []
            
        if newsJson != []:
            artistFound = True
            for entry in newsJson:
                sameTitle = False
                for titleChk in artistNews['stories']:
                    if entry['title'] == titleChk['title']:
                        sameTitle = True

                if not sameTitle:
                    try:
                        newsItem = {}
                        newsItem['title'] = entry['title']
                        newsItem['summary'] = re.sub(r'<.*?>', '', unescape(entry['content']))
                        if len(newsItem['summary']) > 350:
                            newsItem['summary'] = newsItem['summary'][:350] + '...'
                        newsItem['date'] = (re.sub(r'T(.*)$', '', str(entry['pub_date'])))[:10]
                        newsItem['url'] = str(entry['link'])
                        if entry.has_key('publisher'):
                            if entry['publisher'] == 'None':
                                if entry.has_key('feed_link'):
                                    intermsource = re.sub(r'^http(s)*(://)*(www\.)*', '', str(entry['feed_link']), count = 1)
                                    newsItem['articleSource'] = re.sub(r'/(.*)$', '', intermsource, count = 1)
                                else:
                                    newsItem['articleSource'] = ''
                            else:
                                pubString = ChkTxtEnc(entry['publisher'])
                                intermsource = re.sub(r'^http(s)*(://)*(www\.)*', '', pubString, count = 1)
                                newsItem['articleSource'] = re.sub(r'/(.*)$', '', intermsource, count = 1)
                        else:
                            newsItem['articleSource'] = ''
                        newsItem['apiSource'] = 'blinkfire'
                        artistNews['stories'].append(newsItem)
                        if len(artistNews['stories']) >= maxResults:
                            break
                    except Exception:
                        pass


# If there are not enough entries, obtain more entries from echonest
    itemCnt = len(promoNews['stories']) + len(artistNews['stories'])
    if itemCnt < maxResults:
        echonestNewsItems = echonest.GetNewsForArtist(artist)
        if echonestNewsItems != []:
            artistFound = True
            for newsItem in echonestNewsItems:
                sameTitle = False
                for titleChk in artistNews['stories']:
                    if newsItem['title'] == titleChk['title']:
                        sameTitle = True
                if not sameTitle:
                    artistNews['stories'].append(newsItem)
                if len(artistNews['stories']) >= maxResults:
                    break

# Get news stories from google search using custom API only if 'maxResults' number
# news stories wasnt obtained from blinkfire and echonest
    itemCnt = len(promoNews['stories']) + len(artistNews['stories'])
    if itemCnt < maxResults:
        googleSearchUrl = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyD18jSXZ1WtHZZrn9dGaP9ltLfXerY4Ons&cx=015060547345235644646:o3edx1lq9um&q=' + artistName
        try:
            googleJson = RetryLoadJson(googleSearchUrl)
            if googleJson == []:
                if not len(artistNews['stories']) > 0:
                    artistNews['status']['error'] = 'The google search API call timed out'
                    #return artistNews
            if googleJson.has_key('items'):
                counter = 0
                while len(artistNews['stories']) < maxResults and counter <= len(googleJson['items'])-1:
                    newsItem = {}
                    newsItem['title'] = googleJson['items'][counter]['title']
                    sameTitle = False
                    for i, titleChk in enumerate(googleJson['items']):
                        if newsItem['title'] == titleChk[i]['title']:
                            sameTitle = True

                    if not sameTitle:
                        try:
                            newsItem['summary'] = googleJson['items'][counter]['snippet']
                            if len(newsItem['summary']) > 350:
                                newsItem['summary'] = newsItem['summary'][:350] + '...'
                            newsItem['url'] = googleJson['items'][counter]['link']
                            if googleJson['items'][counter].has_key('pagemap'):
                                if googleJson['items'][counter]['pagemap'].has_key('metatags'):
                                    if googleJson['items'][counter]['pagemap']['metatags'].has_key('mtvn_date'):
                                        newsItem['date'] = re.sub(r':(.*)$', '', googleJson['items'][counter]['pagemap']['metatags']['mtvn_date'])
                            newsItem['apiSource'] = 'googleCustomSearch'
                            artistNews['stories'].append(newsItem)
                            artistFound = True
                            artistNews['status']['error'] = 0
                        except Exception:
                            pass
                    counter += 1
        except Exception:
            pass

    if not artistFound:
        artistNews['status']['error'] = 'artist not found'


    if len(artistNews['stories']) > 0:    
        sortedArtistNews = sorted(artistNews['stories'], key=itemgetter('date'), reverse=True)
        artistNews['stories'] = sortedArtistNews

        data = memcache.get('artistNews' + artistName)
        if data is not None:
            memcache.set('artistNews' + artistName, artistNews, 10800)
        else:
            memcache.add('artistNews' + artistName, artistNews, 10800)

        promoNews['stories'][len(promoNews['stories']):] = sortedArtistNews
        artistNews['stories'] = promoNews['stories']
    else:
        artistNews['stories'] = promoNews['stories']
    
    return artistNews
""" --- """



#############################################################################################################################################
class UrlFetchHelper():
    def __init__(self, searchBase, searchArgs):
        self.searchBase = searchBase
        self.searchArgs = searchArgs
        self.syncUrls = []
        self.asyncUrls = []
        self.asyncUrlErrors = []
        self.rpcs = []
        self.asyncResults = []
        self.syncFetchIndex = -1

    def MakeSyncJsonFetch(self, queryKey, queryValue):
        if not self.searchArgs == {}:
            self.baseSearchUrl = self.searchBase + str(urllib.urlencode(self.searchArgs))
            syncUrl = self.baseSearchUrl + '&' + queryKey + "=" + urllib.quote_plus(queryValue)
            self.syncUrls.append(syncUrl)
        else:
            syncUrl = self.searchBase + str(urllib.urlencode({queryKey : queryValue}))
            self.syncUrls.append(syncUrl)
        
        loadedJson = RetryLoadJson(syncUrl)
        
        self.syncFetchIndex += 1    
        return loadedJson

    def handle_result(self, rpc, url):
        result = rpc.get_result()
        if result.status_code == 200:
            self.asyncResults.append(json.loads(result.content))
        else:
            self.asyncUrlErrors.append(url)
            
    def create_callback(self, rpc, url):
        return lambda: self.handle_result(rpc, url)
    
    def MakeAsyncJsonFetch(self, queryKey, queryValues):
        if not self.searchArgs == {}:
            self.baseSearchUrl = self.searchBase + str(urllib.urlencode(self.searchArgs))
            
            for value in queryValues:
                entry = {}
                entry['key'] = value
                searchUrl = self.baseSearchUrl + '&' + queryKey + "=" + urllib.quote_plus(value)
                entry['url'] = searchUrl
                self.asyncUrls.append(entry)
        else:
            for value in queryValues:
                entry = {}
                entry['key'] = value
                searchUrl = self.searchBase + str(urllib.urlencode({queryKey : value}))
                entry['url'] = searchUrl
                self.asyncUrls.append(entry)
                
        for entry in self.asyncUrls:
            url = entry['url']
            rpc = urlfetch.create_rpc(deadline = 10)
            rpc.callback = self.create_callback(rpc, url)
            urlfetch.make_fetch_call(rpc, url)
            self.rpcs.append(rpc)

    def RetrieveAsyncData(self):
        for rpc in self.rpcs:
            rpc.wait()
        return self.asyncResults
""" ------------------------------------------------------------------------------------------------------------------------ """
