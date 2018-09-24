# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class TwitterTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(TwitterTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Twitter Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Twitter Handler")
        
        self.h = httplib2.Http()
        self.twitterResponse, self.twitterContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.twitterJson = json.loads(self.twitterContent)
    
    def urlToTest(self):
        homeResponse, homeContent = self.h.request('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid', 
                                    'GET')
        homeJson = json.loads(homeContent)
        randomArtist = random.choice(homeJson['library'])
        
        magazineResponse, magazineContent = self.h.request(randomArtist['magazine'], 
                                    'GET')
        magazineJson = json.loads(magazineContent)
        self.artistName = magazineJson['name']['corrected']
        return magazineJson['twitter']['json']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url, artistName):
        class TestCaseSubclass(TwitterTestsCase):
            def urlToTest(self):
                self.artistName = artistName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
##    @staticmethod
##    def subclassThatTestsUrl(url, artistName):
##        class TwitterTestsSubclass(TwitterTestsCase):
##            def urlToTest(self):
##                self.artistName = artistName
##                return url
##        return TwitterTestsSubclass
    
    def test_TwitterHandler(self):
        self.log.debug( ' Twitters Tested: ' + self.artistName )
        self.assertEqual('200', self.twitterResponse['status'], msg = self.artistName + ' Twitter Timed out')



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TwitterTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)