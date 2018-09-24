#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python client library for the Facebook Platform.

This client library is designed to support the Graph API and the official
Facebook JavaScript SDK, which is the canonical way to implement
Facebook authentication. Read more about the Graph API at
http://developers.facebook.com/docs/api. You can download the Facebook
JavaScript SDK at http://github.com/facebook/connect-js/.

If your application is using Google AppEngine's webapp framework, your
usage of this module might look like this:

    user = facebook.get_user_from_cookie(self.request.cookies, key, secret)
    if user:
        graph = facebook.GraphAPI(user["access_token"])
        profile = graph.get_object("me")
        friends = graph.get_connections("me", "friends")

"""

import cgi, hashlib, time, urllib, logging
from google.appengine.api import urlfetch
import DataModels as models
import echonestlib as echonest
logging.getLogger().setLevel(logging.DEBUG)


# Find a JSON parser
try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)
from django.utils import simplejson as myjson


class GraphAPI(object):
    """A client for the Facebook Graph API.

    See http://developers.facebook.com/docs/api for complete documentation
    for the API.

    The Graph API is made up of the objects in Facebook (e.g., people, pages,
    events, photos) and the connections between them (e.g., friends,
    photo tags, and event RSVPs). This client provides access to those
    primitive types in a generic way. For example, given an OAuth access
    token, this will fetch the profile of the active user and the list
    of the user's friends:

       graph = facebook.GraphAPI(access_token)
       user = graph.get_object("me")
       friends = graph.get_connections(user["id"], "friends")

    You can see a list of all of the objects and connections supported
    by the API at http://developers.facebook.com/docs/reference/api/.

    You can obtain an access token via OAuth or by using the Facebook
    JavaScript SDK. See http://developers.facebook.com/docs/authentication/
    for details.

    If you are using the JavaScript SDK, you can use the
    get_user_from_cookie() method below to get the OAuth access token
    for the active user from the cookie saved by the SDK.
    """
    def __init__(self, access_token=None):
        self.access_token = access_token

    def get_object(self, id, **args):
        """Fetchs the given object from the graph."""
        return self.request(id, args)

    def get_objects(self, ids, **args):
        """Fetchs all of the given object from the graph.

        We return a map from ID to object. If any of the IDs are invalid,
        we raise an exception.
        """
        args["ids"] = ",".join(ids)
        return self.request("", args)

    def get_connections(self, id, connection_name, **args):
        """Fetchs the connections for given object."""
        return self.request(id + "/" + connection_name, args)

    def put_object(self, parent_object, connection_name, **data):
        """Writes the given object to the graph, connected to the given parent.

        For example,

            graph.put_object("me", "feed", message="Hello, world")

        writes "Hello, world" to the active user's wall. Likewise, this
        will comment on a the first post of the active user's feed:

            feed = graph.get_connections("me", "feed")
            post = feed["data"][0]
            graph.put_object(post["id"], "comments", message="First!")

        See http://developers.facebook.com/docs/api#publishing for all of
        the supported writeable objects.

        Most write operations require extended permissions. For example,
        publishing wall posts requires the "publish_stream" permission. See
        http://developers.facebook.com/docs/authentication/ for details about
        extended permissions.
        """
        assert self.access_token, "Write operations require an access token"
        return self.request(parent_object + "/" + connection_name, post_args=data)

    def put_wall_post(self, message, attachment={}, profile_id="me"):
        """Writes a wall post to the given profile's wall.

        We default to writing to the authenticated user's wall if no
        profile_id is specified.

        attachment adds a structured attachment to the status message being
        posted to the Wall. It should be a dictionary of the form:

            {"name": "Link name"
             "link": "http://www.example.com/",
             "caption": "{*actor*} posted a new review",
             "description": "This is a longer description of the attachment",
             "picture": "http://www.example.com/thumbnail.jpg"}

        """
        return self.put_object(profile_id, "feed", message=message, **attachment)

    def put_comment(self, object_id, message):
        """Writes the given comment on the given post."""
        return self.put_object(object_id, "comments", message=message)

    def put_like(self, object_id):
        """Likes the given post."""
        return self.put_object(object_id, "likes")

    def delete_object(self, id):
        """Deletes the object with the given ID from the graph."""
        self.request(id, post_args={"method": "delete"})

    def request(self, path, args=None, post_args=None):
        """Fetches the given path in the Graph API.

        We translate args to a valid query string. If post_args is given,
        we send a POST request to the given path with the given arguments.
        """
        if not args: args = {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)
        file = urllib.urlopen("https://graph.facebook.com/" + path + "?" +
                              urllib.urlencode(args), post_data)
        try:
            response = _parse_json(file.read())
        finally:
            file.close()
        if response.get("error"):
            raise GraphAPIError(response["error"]["type"],
                                response["error"]["message"])
        return response
  
    def Batch_Profile_Request(self, ids):
        """ Recieves a list of artist names as an input and returns an dictionary of
            entries using profile id as the key and a dictionary entry as the value
            with the following keys:
            name : profile name
            image : profile picture
            id : profile id
            url : profile url"""
        post_args = {}
        post_args["access_token"] = self.access_token
        url = "https://graph.facebook.com/"
        allProfiles = {}
        rpcs = []

        idString = ''
        for index, facebookID in enumerate(ids):
            idString = idString + facebookID
            if index == (len(ids) - 1) or ((index+1)%50 == 0):
                batchRequest = [{"method" : "GET", "relative_url" : "?ids=" + idString}]
                JsonRequest = myjson.dumps(batchRequest)
                post_args["batch"] = JsonRequest
                post_data = urllib.urlencode(post_args)
                AppendProfileRPC(rpcs, url, post_data, allProfiles)
                idString = ''
            else:
                idString = idString + ','

        for rpc in rpcs:
            rpc.wait()
            
        return allProfiles

    def Batch_Music_Likes_Request(self, ids):
        """ Recieves a list of artist names as an input and returns an dictionary of
            entries using profile id as the key and a dictionary entry as the value
            with the following keys:
            'music likes' : array of music likes"""
        post_args = {}
        post_args["access_token"] = self.access_token
        url = "https://graph.facebook.com/"
        allMusicLikes = {}
        rpcs = []

        idString = ''
        for index, facebookID in enumerate(ids):
            idString = idString + facebookID
            if index == (len(ids) - 1) or ((index+1)%50 == 0):
                batchRequest = [{"method" : "GET", "relative_url" : "music?ids=" + idString}]
                JsonRequest = myjson.dumps(batchRequest)
                post_args["batch"] = JsonRequest
                post_data = urllib.urlencode(post_args)
                AppendMusicLikesRPC(rpcs, url, post_data, allMusicLikes)
                idString = ''
            else:
                idString = idString + ','

        for rpc in rpcs:
            rpc.wait()
            
        return allMusicLikes

    def Batch_Profile_And_Likes_Request(self, ids):
        """ Recieves a list of artist names as an input and returns an dictionary of
            entries using profile id as the key and a dictionary entry as the value
            with the following keys:
            'music likes' : array of music likes"""
        logging.info('Start getting profile and likes info')
        post_args = {}
        post_args["access_token"] = self.access_token
        url = "https://graph.facebook.com/"
        allProfileData = {}
        rpcs = []

        idString = ''
        for index, facebookID in enumerate(ids):
            idString = idString + facebookID
            if index == (len(ids) - 1) or ((index+1)%50 == 0):
                batchRequest = [{"method" : "GET", "relative_url" : "music?ids=" + idString}, {"method" : "GET", "relative_url" : "?ids=" + idString}]
                JsonRequest = myjson.dumps(batchRequest)
                post_args["batch"] = JsonRequest
                post_data = urllib.urlencode(post_args)
                AppendProfileandMusicLikesRPC(rpcs, url, post_data, allProfileData)
                idString = ''
            else:
                idString = idString + ','

        for rpc in rpcs:
            rpc.wait()

        logging.info('Finished getting profile and likes info')
        return allProfileData


""" Helper functions for the GraphAPI.Batch_Profile_Request and GraphAPI.Batch_Music_Likes_Request methods"""
def AppendProfileRPC(rpcs, url, post_data, allProfiles):
    rpc = urlfetch.create_rpc(deadline = 10)
    rpc.callback = ProfileAsyncCallback(rpc, rpcs, url, post_data, allProfiles)
    urlfetch.make_fetch_call(rpc, url, payload=post_data, method='POST')
    rpcs.append(rpc)

def ProfileAsyncCallback(rpc, rpcs, url, post_data, allProfiles):
    return lambda: HandleProfileAsyncCallback(rpc, rpcs, url, post_data, allProfiles)

def HandleProfileAsyncCallback(rpc, rpcs, url, post_data, allProfiles):
    try:
        profileResults = rpc.get_result()
        if profileResults.status_code == 200:
            profileResultsData = myjson.loads(profileResults.content)
            batchOfProfiles = myjson.loads(profileResultsData[0]['body'])
            for profile in batchOfProfiles:
                profileEntry = {}
                profileEntry['name'] = batchOfProfiles[profile]["name"]
                profileEntry['url'] = batchOfProfiles[profile]["link"]
                profileEntry['id'] = batchOfProfiles[profile]["id"]
                profileEntry['image'] = "http://graph.facebook.com/" + batchOfProfiles[profile]["id"] + "/picture?type=square"
                allProfiles[profileEntry['id']] = profileEntry
        else:
            AppendProfileRPC(rpcs, url, post_data, allProfiles)
    except urlfetch.DeadlineExceededError:
        AppendProfileRPC(rpcs, url, post_data, allProfiles)

def AppendMusicLikesRPC(rpcs, url, post_data, allMusicLikes):
    rpc = urlfetch.create_rpc(deadline = 10)
    rpc.callback = MusicLikesAsyncCallback(rpc, rpcs, url, post_data, allMusicLikes)
    urlfetch.make_fetch_call(rpc, url, payload=post_data, method='POST')
    rpcs.append(rpc)

def MusicLikesAsyncCallback(rpc, rpcs, url, post_data, allMusicLikes):
    return lambda: HandleMusicLikesAsyncCallback(rpc, rpcs, url, post_data, allMusicLikes)

def HandleMusicLikesAsyncCallback(rpc, rpcs, url, post_data, allMusicLikes):
    try:
        musicLikesResults = rpc.get_result()
        if musicLikesResults.status_code == 200:
            musicLikesResultsData = myjson.loads(musicLikesResults.content)
            batchOfMusicLikes = myjson.loads(musicLikesResultsData[0]['body'])
            for profile in batchOfMusicLikes:
                musicLikes = []
                if batchOfMusicLikes[profile]['data'] != []:
                    for artist in batchOfMusicLikes[profile]['data']:
                        if artist['category'] == "Musician/band":
                            musicLikes.append(artist['name'])
                allMusicLikes[profile] = musicLikes
        else:
            AppendMusicLikesRPC(rpcs, url, post_data, allMusicLikes)
    except urlfetch.DeadlineExceededError:
        AppendMusicLikesRPC(rpcs, url, post_data, allMusicLikes)



def AppendProfileandMusicLikesRPC(rpcs, url, post_data, allProfileData):
    rpc = urlfetch.create_rpc(deadline = 10)
    rpc.callback = ProfileandMusicLikesAsyncCallback(rpc, rpcs, url, post_data, allProfileData)
    urlfetch.make_fetch_call(rpc, url, payload=post_data, method='POST')
    rpcs.append(rpc)

def ProfileandMusicLikesAsyncCallback(rpc, rpcs, url, post_data, allProfileData):
    return lambda: HandleProfileandMusicLikesAsyncCallback(rpc, rpcs, url, post_data, allProfileData)

def HandleProfileandMusicLikesAsyncCallback(rpc, rpcs, url, post_data, allProfileData):
    try:
        facebookResponse = rpc.get_result()
        if facebookResponse.status_code == 200:
            facebookResponseData = myjson.loads(facebookResponse.content)
            batchOfProfiles = myjson.loads(facebookResponseData[1]['body'])
            batchOfMusicLikes = myjson.loads(facebookResponseData[0]['body'])
            if len(batchOfProfiles) == len(batchOfMusicLikes):
                for profile in batchOfProfiles:
                    profileEntry = {}
                    profileEntry['name'] = batchOfProfiles[profile]["name"]
                    profileEntry['url'] = batchOfProfiles[profile]["link"]
                    profileEntry['id'] = batchOfProfiles[profile]["id"]
                    profileEntry['image'] = "http://graph.facebook.com/" + batchOfProfiles[profile]["id"] + "/picture?type=square"
                    profileEntry['music likes'] = []
                    friendFacebookUser = models.FacebookUser.get_by_key_name(batchOfProfiles[profile]["id"])
                    if friendFacebookUser is None:
                        friendFacebookUser = models.FacebookUser(key_name = batchOfProfiles[profile]["id"],
                                                                 name = batchOfProfiles[profile]["name"],
                                                                 profile_url = batchOfProfiles[profile]["link"],
                                                                 fbArtistList = [])

                    else:
                        #logging.info( 'Friend ' + str(batchOfProfiles[profile]["id"]) + ' is already in datastore')
                        friendFacebookUser.fbArtistList = []
                        friendFacebookUser.put()
                        
                    rawMusicLikes = []
                    if batchOfMusicLikes[profile]['data'] != []:
                        for artist in batchOfMusicLikes[profile]['data']:
                            if artist['category'] == "Musician/band":
                                rawMusicLikes.append(artist['name'])
                    if rawMusicLikes != []:
                        correctedFacebookFavorites = echonest.CorrectArtistNames(rawMusicLikes)
                        #if retStatus == 'Timed Out':
                        #    logging.info( 'It got to the timeout')
                        #    break
                        for artist in correctedFacebookFavorites:
                            if artist != None:
                                profileEntry['music likes'].append(artist)

                        if len(profileEntry['music likes']) > 0:
                            friendFacebookUser.fbArtistList = profileEntry['music likes']
                        else:
                            friendFacebookUser.fbArtistList = []
                            friendFacebookUser.fbArtistListString = ""
                            logging.info( 'Friend ' + str(batchOfProfiles[profile]["id"]) + ',' + str(batchOfProfiles[profile]["name"].encode('utf-8')) + ' had no correct music likes')
                            logging.info(rawMusicLikes)
                        friendFacebookUser.put()
                    else:
                        friendFacebookUser.fbArtistList = []
                        friendFacebookUser.fbArtistListString = ""
                        friendFacebookUser.put()
                        logging.info( 'Friend ' + str(batchOfProfiles[profile]["id"]) + ',' + str(batchOfProfiles[profile]["name"].encode('utf-8')) + ' has no music likes')

                    allProfileData[profileEntry['id']] = profileEntry
            else:
                logging.info( 'bad response from facebook, reappending')
                AppendProfileandMusicLikesRPC(rpcs, url, post_data, allProfileData)
        else:
            logging.info(str(facebookResponse.status_code) + ' code on facebook request, reappending')
            AppendProfileandMusicLikesRPC(rpcs, url, post_data, allProfileData)
    except urlfetch.DeadlineExceededError:
        logging.info('urlfetch deadline of 10 seconds exceeded on facebook request, reappending')
        AppendProfileandMusicLikesRPC(rpcs, url, post_data, allProfileData)
""" --- """
    
class GraphAPIError(Exception):
    def __init__(self, type, message):
        Exception.__init__(self, message)
        self.type = type


def get_user_from_cookie(cookies, app_id, app_secret):
    """Parses the cookie set by the official Facebook JavaScript SDK.

    cookies should be a dictionary-like object mapping cookie names to
    cookie values.

    If the user is logged in via Facebook, we return a dictionary with the
    keys "uid" and "access_token". The former is the user's Facebook ID,
    and the latter can be used to make authenticated requests to the Graph API.
    If the user is not logged in, we return None.

    Download the official Facebook JavaScript SDK at
    http://github.com/facebook/connect-js/. Read more about Facebook
    authentication at http://developers.facebook.com/docs/authentication/.
    """
    cookie = cookies.get("fbsr_" + app_id, "")
    if not cookie: return None, 'poop'
    args = dict((k, v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items())
    payload = "".join(k + "=" + args[k] for k in sorted(args.keys())
                      if k != "sig")
    sig = hashlib.md5(payload + app_secret).hexdigest()
    expires = int(args["expires"])
    if sig == args.get("sig") and (expires == 0 or time.time() < expires):
        return args, 'good'
    else:
        return None, 'good'
