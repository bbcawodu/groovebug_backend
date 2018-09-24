# -*- coding: utf-8 -*-
import unittest, httplib2, random, logging, sys
from django.utils import simplejson as json

class CompositeTestsCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(CompositeTestsCase, self).__init__(methodName)
        logging.basicConfig(stream=sys.stderr)
        logging.getLogger("Composite Handler").setLevel(logging.DEBUG)
        self.log = logging.getLogger("Composite Handler")
        
        self.h = httplib2.Http()
        self.compositeResponse, self.compositeContent = self.h.request(self.urlToTest(), 
                                    'GET',)
        self.compositeJson = json.loads(self.compositeContent)
        
    def urlToTest(self):
        featuredResponse, featuredContent = self.h.request('http://backendgroovebug.appspot.com/v2/featured?user=bradstestudid', 
                                    'GET')
        featuredJson = json.loads(featuredContent)
        randomTile = random.choice(featuredJson['tiles'])
        
        self.compositeName = randomTile['name']
        return randomTile['composite']
    
    @staticmethod
    def addToSuites(suites, url, compositeName):
        class TestCaseSubclass(CompositeTestsCase):
            def urlToTest(self):
                self.compositeName = compositeName
                return url
            def suiteList(self):
                return suites
            
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseSubclass)
        suites.append(suite)
    
    def test_CompositeHandler(self):
        self.log.debug(' Composite Tested: ' + self.compositeName)
        
        self.assertEqual('200', self.compositeResponse['status'], msg = self.compositeName + ' Tile Timed out')
        self.assertEqual('0', self.compositeJson['status']['error'], msg = self.compositeName + ' Tile Failed')


            
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CompositeTestsCase)
    unittest.TextTestRunner(verbosity=2).run(suite)