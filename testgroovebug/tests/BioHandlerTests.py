# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class BioTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(BioTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Bio Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Bio Handler")
        
        self.h = httplib2.Http()
        self.bioResponse, self.bioContent = self.h.request(self.urlToTest(), 
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
        return magazineJson['bio']['html']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url, artistName):
        class TestCaseSubclass(BioTestsCase):
            def urlToTest(self):
                self.artistName = artistName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
    def test_BioHandler(self):
        self.log.debug( ' Bio Tested: ' + self.artistName )
        self.assertEqual('200', self.bioResponse['status'], msg = self.artistName + ' Bio Timed out')


            
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BioTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)