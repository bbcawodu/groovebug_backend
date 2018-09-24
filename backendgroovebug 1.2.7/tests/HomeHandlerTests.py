# -*- coding: utf-8 -*-
import unittest, httplib2, random, FeaturedHandlerTests, FacebookFriendsHandlerTests, MagazineHandlerTests
from django.utils import simplejson as json
#import os, sys

class HomeTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
##        unittest.TestCase.__init__(self, methodName)
        super(HomeTestsCase,self).__init__(methodName)
        jsonFile = open('home post.json', 'r')
        postDict = json.loads(jsonFile.read())
        self.longPost = json.dumps(postDict)
        self.h = httplib2.Http()
        self.homeResponse, self.homeContent = self.h.request(self.urlToTest(), 
                                    'POST', 
                                    self.longPost,
                                    headers={'Content-Type': 'application/json'})
        self.homeJson = json.loads(self.homeContent)
        ##HomeTestsCase.homeJson = self.homeJson

    def urlToTest(self):
        return 'http://backendgroovebug.appspot.com/v2/home?user=bradstestudid&fbauth=AAACWxMASSIcBAGyxJOersM9vnhy4ZAxgakzmN23WLIGBdz2CrAvjZAM5qGGtZAWFhXFqjWjNLoD4ZCpzPomLRNGouqmDF9YZD'
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
    
    @staticmethod
    def addToSuites(suites, url):
        class TestCaseSubclass(HomeTestsCase):
            def urlToTest(self):
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)

    def test_ZLinks(self):
        FeaturedHandlerTests.FeaturedTestsCase.addToSuites(self.suiteList(), self.homeJson['featured'])
        FacebookFriendsHandlerTests.FacebookFriendsTestsCase.addToSuites(self.suiteList(), self.homeJson['friends'])
        randomArtists = random.sample(self.homeJson['library'], 3)
        for artist in randomArtists:
            MagazineHandlerTests.MagazineTestsCase.addToSuites(self.suiteList(), artist['magazine'])
                
## Tests if a POST to the verification handler gives a 200 response
    def test_HomeHandlerVersion2Post(self):
        self.assertEqual('200', self.homeResponse['status'], msg = 'Home Handler timed out')
        self.assertEqual('0', self.homeJson['status']['error'], msg = 'Home Handler Error')
        
"""
    @staticmethod
    def subclassThatTestsUrl(url):
        class HomeTestsSubclass(HomeTestsCase):
            def urlToTest(self):
                return url
        return HomeTestsSubclass
        
    @classmethod
    def tearDownClass(HomeTestsCase):
        suite = unittest.TestSuite()
        
        featuredTestClass = FeaturedHandlerTests.FeaturedTestsCase.subclassThatTestsUrl(HomeTestsCase.homeJson['featured'])
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(featuredTestClass))
        
        facebookFriendsTestClass = FacebookFriendsHandlerTests.FacebookFriendsTestsCase.subclassThatTestsUrl(HomeTestsCase.homeJson['friends'])
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(facebookFriendsTestClass))
        
        unittest.TextTestRunner(verbosity=2).run(suite)
        
        randomArtists = random.sample(HomeTestsCase.homeJson['library'], 3)
        for artist in randomArtists:
            magazineTestClass = MagazineHandlerTests.MagazineTestsCase.subclassThatTestsUrl(artist['magazine'])
            magazineTestSuite = unittest.TestLoader().loadTestsFromTestCase(magazineTestClass)
            unittest.TextTestRunner(verbosity=2).run(magazineTestSuite)
"""

            
if __name__ == '__main__':
    suites = []
    
    HomeTestsCase.addToSuites(suites, 'http://backendgroovebug.appspot.com/v2/home?user=bradstestudid&fbauth=AAACWxMASSIcBAGyxJOersM9vnhy4ZAxgakzmN23WLIGBdz2CrAvjZAM5qGGtZAWFhXFqjWjNLoD4ZCpzPomLRNGouqmDF9YZD')

    for suite in suites:
        unittest.TextTestRunner(verbosity=2).run(suite)
            
    """
    testClass = HomeTestsCase.subclassThatTestsUrl('http://backendgroovebug.appspot.com/v2/home?user=bradstestudid&fbauth=AAACWxMASSIcBAGyxJOersM9vnhy4ZAxgakzmN23WLIGBdz2CrAvjZAM5qGGtZAWFhXFqjWjNLoD4ZCpzPomLRNGouqmDF9YZD')
    suite = unittest.TestLoader().loadTestsFromTestCase(testClass)
    unittest.TextTestRunner(verbosity=2).run(suite)
    """
    