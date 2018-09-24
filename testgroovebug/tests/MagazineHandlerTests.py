# -*- coding: utf-8 -*-
import unittest, logging, sys, httplib2, random, BioHandlerTests, BackgroundHandlerTests, MusicHandlerTests, NewsHandlerTests
import SimilarHandlerTests, TwitterHandlerTests, VideoHandlerTests
from django.utils import simplejson as json

class MagazineTestsCase(unittest.TestCase):              
    def __init__(self, methodName='runTest'):
        super(MagazineTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Magazine Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Magazine Handler")
        
        self.h = httplib2.Http()
        self.artistResponse, self.artistContent = self.h.request(self.urlToTest(), 
                                'GET',)
        self.magazineJson = json.loads(self.artistContent)
        self.artistName = self.magazineJson['name']['corrected']
        
    
    def urlToTest(self):
        homeResponse, homeContent = self.h.request('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid', 
                                    'GET')
        homeJson = json.loads(homeContent)
        randomArtist = random.choice(homeJson['library'])
        return randomArtist['magazine']
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url):
        class TestCaseSubclass(MagazineTestsCase):
            def urlToTest(self):
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
    def test_MagazineHandler(self):
        self.log.debug( ' Magazine Tested: ' + self.artistName )
        
        self.assertEqual('200', self.artistResponse['status'], msg = self.artistName + ' Magazine Timed out')
        self.assertEqual('0', self.magazineJson['status']['error'], msg = self.artistName + ' Magazine Failed')
        
    def test_ZLinks(self):
        BioHandlerTests.BioTestsCase.addToSuites(self.suiteList(), self.magazineJson['bio']['html'], self.artistName)
        BackgroundHandlerTests.BackgroundsTestsCase.addToSuites(self.suiteList(), self.magazineJson['backgrounds']['json'], self.artistName)
        MusicHandlerTests.MusicTestsCase.addToSuites(self.suiteList(), self.magazineJson['music']['json'], self.artistName)
        NewsHandlerTests.NewsTestsCase.addToSuites(self.suiteList(), self.magazineJson['news']['html'], self.artistName)
        SimilarHandlerTests.SimilarTestsCase.addToSuites(self.suiteList(), self.magazineJson['similar']['json'], self.artistName)
        TwitterHandlerTests.TwitterTestsCase.addToSuites(self.suiteList(), self.magazineJson['twitter']['json'], self.artistName)
        VideoHandlerTests.VideosTestsCase.addToSuites(self.suiteList(), self.magazineJson['videos']['html'], self.artistName)
            

            
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(MagazineTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)