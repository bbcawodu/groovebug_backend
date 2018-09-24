# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class SimilarTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(SimilarTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Similar Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Similar Handler")
        
        self.h = httplib2.Http()
        self.similarResponse, self.similarContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.similarJson = json.loads(self.similarContent)
        
    def urlToTest(self):
        homeResponse, homeContent = self.h.request('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid', 
                                    'GET')
        homeJson = json.loads(homeContent)
        randomArtist = random.choice(homeJson['library'])
        
        magazineResponse, magazineContent = self.h.request(randomArtist['magazine'], 
                                    'GET')
        magazineJson = json.loads(magazineContent)
        self.artistName = magazineJson['name']['corrected']
        return magazineJson['similar']['json']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url, artistName):
        class TestCaseSubclass(SimilarTestsCase):
            def urlToTest(self):
                self.artistName = artistName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
##    @staticmethod
##    def subclassThatTestsUrl(url, artistName):
##        class SimilarTestsSubclass(SimilarTestsCase):
##            def urlToTest(self):
##                self.artistName = artistName
##                return url
##        return SimilarTestsSubclass
        
    def test_SimilarArtistHandler(self):
        self.log.debug( ' Similar Artists Tested: ' + self.artistName )
        self.assertEqual('200', self.similarResponse['status'], msg = self.artistName + ' Similar Artists Timed out')
        self.assertEqual('0', self.similarJson['status']['error'], self.artistName + ' Similar Artists Failed')
        


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimilarTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)