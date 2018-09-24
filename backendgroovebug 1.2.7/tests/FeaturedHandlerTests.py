# -*- coding: utf-8 -*-
import unittest, httplib2, CompositeHandlerTests, random
from django.utils import simplejson as json

class FeaturedTestsCase(unittest.TestCase):      
    def __init__(self, methodName='runTest'):
        super(FeaturedTestsCase,self).__init__(methodName)
        self.h = httplib2.Http()
        self.featuredResponse, self.featuredContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.featuredJson = json.loads(self.featuredContent)
        
    
    def urlToTest(self):
        return 'http://backendgroovebug.appspot.com/v2/featured?user=bradstestudid'
    
    def suiteList(self):
        raise Exception, 'Not yet implemented'
        
    @staticmethod
    def addToSuites(suites, url):
        class TestCaseSubclass(FeaturedTestsCase):
            def urlToTest(self):
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
##    @classmethod
##    def tearDownClass(MagazineTestsClass):
##        suite = unittest.TestSuite()
##        
##        randomComposites = random.sample(FeaturedTestsCase.featuredJson['tiles'], 3)
##        for composite in randomComposites:
##            compositeTestClass = CompositeHandlerTests.CompositeTestsCase.subclassThatTestsUrl(composite['composite'], composite['name'])
##            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(compositeTestClass))
##        
##        unittest.TextTestRunner(verbosity=2).run(suite)
    
    def test_FeaturedHandler(self):
        self.assertEqual('200', self.featuredResponse['status'], msg = 'Featured Handler Timeout')
        self.assertEqual('0', self.featuredJson['status']['error'], msg = 'Featured Handler Error')
        
    def test_ZLinks(self):
        randomComposites = random.sample(self.featuredJson['tiles'], 3)
        for composite in randomComposites:
            CompositeHandlerTests.CompositeTestsCase.addToSuites(self.suiteList(), composite['composite'], composite['name'])


            
if __name__ == '__main__':
    suites = []
    
    FeaturedTestsCase.addToSuites(suites, 'http://backendgroovebug.appspot.com/v2/featured?user=bradstestudid')
    for suite in suites:
        unittest.TextTestRunner(verbosity=2).run(suite)