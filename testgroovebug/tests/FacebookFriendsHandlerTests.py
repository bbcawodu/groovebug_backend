# -*- coding: utf-8 -*-
import unittest, httplib2
from django.utils import simplejson as json

class FacebookFriendsTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(FacebookFriendsTestsCase, self).__init__(methodName)
        self.h = httplib2.Http()
        self.facebookResponse, self.facebookContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.facebookJson = json.loads(self.facebookContent)
    
    def urlToTest(self):
        return 'http://backendgroovebug.appspot.com/v2/friends?user=bradstestudid&fbauth=AAACWxMASSIcBAGyxJOersM9vnhy4ZAxgakzmN23WLIGBdz2CrAvjZAM5qGGtZAWFhXFqjWjNLoD4ZCpzPomLRNGouqmDF9YZD'
    
    @staticmethod
    def subclassThatTestsUrl(url):
        class FeaturedTestsSubclass(FacebookFriendsTestsCase):
            def urlToTest(self):
                return url
        return FeaturedTestsSubclass
    
    @staticmethod
    def addToSuites(suites, url):
        class TestCaseSubclass(FacebookFriendsTestsCase):
            def urlToTest(self):
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
    def test_FacebookFriendsHandler(self):
        self.assertEqual('200', self.facebookResponse['status'], msg = 'Facebook Friends Handler Timeout')
        self.assertEqual('0', self.facebookJson['status']['error'], msg = 'Facebook Friends Handler Error')
   

            
if __name__ == '__main__':
    suites = []
    
    FacebookFriendsTestsCase.addToSuites(suites, 'http://backendgroovebug.appspot.com/v2/friends?user=bradstestudid&fbauth=AAACWxMASSIcBAGyxJOersM9vnhy4ZAxgakzmN23WLIGBdz2CrAvjZAM5qGGtZAWFhXFqjWjNLoD4ZCpzPomLRNGouqmDF9YZD')
    for suite in suites:
        unittest.TextTestRunner(verbosity=2).run(suite)