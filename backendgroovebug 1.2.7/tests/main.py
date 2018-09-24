import unittest
import BackgroundHandlerTests, BioHandlerTests, CompositeHandlerTests, FacebookFriendsHandlerTests, FeaturedHandlerTests
import HomeHandlerTests, MagazineHandlerTests, MusicHandlerTests, NewsHandlerTests, SimilarHandlerTests
import TwitterHandlerTests, VideoHandlerTests

testModules = []
testModules.append(HomeHandlerTests)
testModules.append(FeaturedHandlerTests)
testModules.append(FacebookFriendsHandlerTests)
testModules.append(MagazineHandlerTests)
testModules.append(BackgroundHandlerTests)
testModules.append(BioHandlerTests)
testModules.append(CompositeHandlerTests)
testModules.append(MusicHandlerTests)
testModules.append(NewsHandlerTests)
testModules.append(SimilarHandlerTests)
testModules.append(TwitterHandlerTests)
testModules.append(VideoHandlerTests)

allTestSuites = []
for testModule in testModules:
    allTestSuites.append(testModule.loadTestSuite())



if __name__ == '__main__':
    alltests = unittest.TestSuite(allTestSuites)
    unittest.TextTestRunner(verbosity=2).run(alltests)