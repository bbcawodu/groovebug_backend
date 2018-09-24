""" This Handler is responsible for recieving a name of a
    composite name from the url wrapper, and returning a
    Json document with information about the composite
    the wrapper for this page is
    http://backendgroovebug.appspot.com/v1/composite?name="""



import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from os import path
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils.html import linebreaks
from django.utils import simplejson as json
from google.appengine.api import memcache
import DataModels as models
import echonestlib as echonest
import logging
logging.getLogger().setLevel(logging.DEBUG)



""" Class that handles composite request"""
class CompositeHandler(webapp.RequestHandler):
    def get(self, name):
        compositeName = self.request.get('name')
        compositeData = models.GetCompositeData(compositeName)
        compositeJson = json.dumps(compositeData)
    
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(compositeJson)                
""" --- """



""" Class that handles composite request"""
class CompositeHTMLHandler(webapp.RequestHandler):
    def get(self, name):
        logging.info('START')
        compositeId = self.request.get('id')
        compositeId = int(compositeId)
        html = None

        if compositeId:
            html = memcache.get('CompositeHTML' + str(compositeId))
            if html is None:
                compositePage = models.CompositePage.get_by_id(compositeId)
                
                if compositePage is None:
                    self.response.out.write('FAIL')
                else:
                    compPage = {}
                    compPage['summary'] = linebreaks(compositePage.summary)
                    compPage['title'] = compositePage.title
                    if compositePage.graphicUrl != 'N/A':
                        compPage['graphicUrl'] = compositePage.graphicUrl
                    else:
                        compPage['graphicUrl'] = 'http://' + str(hostUrl) + '/v1/backgrounds?artist=blank+images'
                    if compositePage.summaryUrl != 'N/A':
                        compPage['summaryUrl'] = compositePage.summaryUrl
                    compPage['compPageId'] = self.request.get('compositeid')

                    newsArticles = []
                    artistListLength = len(compositePage.artistList)
                    for index, artist in enumerate(compositePage.artistList):
                        logging.info('Getting 3 news articles for artist ' + str(index) + ' of ' + str(artistListLength))
                        artistData = models.GetArtistNews(artist, maxResults = 3)
                        if artistData['status']['error'] == '0':
                            for newsItem in artistData['stories']:
                                if newsItem.has_key('date'):
                                    newsArticles.append(newsItem)
                    newsArticles.sort(key=lambda item:item['date'], reverse=True)
                    sortedArticles = []
                    for index, article in enumerate(newsArticles):
                        if index == 20:
                            break
                        sortedArticles.append(article)
                    if sortedArticles != []:
                        compPage['newsArticles'] = sortedArticles
                        
                    context = {'compPage' : compPage,}
                    tmpl = path.join(path.dirname(__file__), 'compositeHTML.html')
                    html = render(tmpl, context)
                    SetCompositeHTMLMemcache(compositeId, html)
                    logging.info('FINISH')
                    self.response.out.write(html)
            else:
                self.response.out.write(html)
        else:
            self.response.out.write('FAIL')
""" --- """

def SetCompositeHTMLMemcache(compID, compHTML):
    data = memcache.get('CompositeHTML' + str(compID))
    if data is not None:
        memcache.set('CompositeHTML' + str(compID), compHTML, 3600*3)
    else:
        memcache.add('CompositeHTML' + str(compID), compHTML, 3600*3)

""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/compositehtml(.*)', CompositeHTMLHandler),
                                      ('/v1/composite(.*)', CompositeHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
