# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class BackgroundsTestsCase(unittest.TestCase):    
    def __init__(self, methodName='runTest'):
        super(BackgroundsTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Backgrounds Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Backgrounds Handler")
        
        self.h = httplib2.Http()
        self.backgroundsResponse, self.backgroundsContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.backgroundsJson = json.loads(self.backgroundsContent)
    
    def urlToTest(self):
        homeResponse, homeContent = self.h.request('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid', 
                                    'GET')
        homeJson = json.loads(homeContent)
        randomArtist = random.choice(homeJson['library'])
        
        magazineResponse, magazineContent = self.h.request(randomArtist['magazine'], 
                                    'GET')
        magazineJson = json.loads(magazineContent)
        self.artistName = magazineJson['name']['corrected']
        return magazineJson['backgrounds']['json']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url, artistName):
        class TestCaseSubclass(BackgroundsTestsCase):
            def urlToTest(self):
                self.artistName = artistName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
        
    def test_BackgroundHandler(self):
        self.log.debug(' Backgounds Tested: ' + self.artistName)
        
        self.assertEqual('200', self.backgroundsResponse['status'], msg = self.artistName + ' Backgrounds Timed out')
        self.assertEqual('0', self.backgroundsJson['status']['error'], msg = self.artistName + ' Backgrounds Failed')
        


            
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BackgroundsTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)