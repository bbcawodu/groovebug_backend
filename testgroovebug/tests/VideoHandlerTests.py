# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class VideosTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(VideosTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Videos Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Videos Handler")
        
        self.h = httplib2.Http()
        self.videosResponse, self.videosContent = self.h.request(self.urlToTest(), 
                                    'GET',)
    
    def urlToTest(self):
        homeResponse, homeContent = self.h.request('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid', 
                                    'GET')
        homeJson = json.loads(homeContent)
        randomArtist = random.choice(homeJson['library'])
        
        magazineResponse, magazineContent = self.h.request(randomArtist['magazine'], 
                                    'GET')
        magazineJson = json.loads(magazineContent)
        self.artistName = magazineJson['name']['corrected']
        return magazineJson['videos']['html']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url, artistName):
        class TestCaseSubclass(VideosTestsCase):
            def urlToTest(self):
                self.artistName = artistName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
##    @staticmethod
##    def subclassThatTestsUrl(url, artistName):
##        class VideosTestsSubclass(VideosTestsCase):
##            def urlToTest(self):
##                self.artistName = artistName
##                return url
##        return VideosTestsSubclass
    
    def test_VideoHandler(self):
        self.log.debug( ' Videos Tested: ' + self.artistName  )
        self.assertEqual('200', self.videosResponse['status'], msg = self.artistName + ' Video Timed out')
        


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(VideosTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)