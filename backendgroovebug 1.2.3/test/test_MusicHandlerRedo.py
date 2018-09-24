# -*- coding: utf-8 -*-
import unittest
import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.api import urlfetch
from google.appengine.ext import testbed, webapp
import urllib2, urllib, datetime
from django.utils import simplejson as json
from webtest import TestApp
import DataModels as models
import MusicHandlerRedo

class MusicTester(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        self.testbed.init_urlfetch_stub()
        self.application = webapp.WSGIApplication([('/(.*)', MusicHandlerRedo.MusicHandler)], debug=True)

    def tearDown(self):
        self.testbed.deactivate()
        
## Tests artist Eminem to see if Music Handler gives a 200 response        
    def test_fortimeout(self):
        app = TestApp(self.application)
        response = app.get('/?artist=Eminem')
        self.assertEqual('200 OK', response.status)

## Tests artist Eminem to see if Music Handler no errors within the JSON response 
    def test_forJsonErrors(self):
        app = TestApp(self.application)
        response = app.get('/?artist=Eminem')
        artistJson = json.loads(response.body)
        self.assertEqual('0', artistJson['status']['error'])

## Tests artist Eminem to see if the album 'recovery' exists
    def test_EminemForRecoveryAlbum(self):
        app = TestApp(self.application)
        response = app.get('/?artist=Eminem')
        artistJson = json.loads(response.body)
        
        albums = []
        for album in artistJson['albums']:
            albums.append(album['title'])
            
        self.assertTrue('Recovery' in albums)

## Tests artist múm to see if Music Handler gives a 200 response  
    def test_forUnicodeArtist(self):
        app = TestApp(self.application)
        response = app.get(u'/?artist=múm')
        artistJson = json.loads(response.body)
        self.assertEqual('0', artistJson['status']['error'])
                

