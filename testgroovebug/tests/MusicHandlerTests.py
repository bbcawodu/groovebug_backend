# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class MusicTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(MusicTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Music Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Music Handler")
        
        self.h = httplib2.Http()
        self.musicResponse, self.musicContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.musicJson = json.loads(self.musicContent)
        
    def urlToTest(self):
        homeResponse, homeContent = self.h.request('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid', 
                                    'GET')
        homeJson = json.loads(homeContent)
        randomArtist = random.choice(homeJson['library'])
        
        magazineResponse, magazineContent = self.h.request(randomArtist['magazine'], 
                                    'GET')
        magazineJson = json.loads(magazineContent)
        self.artistName = magazineJson['name']['corrected']
        return magazineJson['music']['json']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url, artistName):
        class TestCaseSubclass(MusicTestsCase):
            def urlToTest(self):
                self.artistName = artistName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
        
##    @staticmethod
##    def subclassThatTestsUrl(url, artistName):
##        class MusicTestsSubclass(MusicTestsCase):
##            def urlToTest(self):
##                self.artistName = artistName
##                return url
##        return MusicTestsSubclass
    
    def test_MusicHandler(self):
        self.log.debug( ' Music Tested: ' + self.artistName )
        self.assertEqual('200', self.musicResponse['status'], msg = self.artistName + ' Music Timed out')
        self.assertEqual('0', self.musicJson['status']['error'], msg = self.artistName + ' Music Failed')



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(MusicTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)