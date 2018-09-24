""" This Handler is responsible for making the API calls, parsing the
    json data for a given artist, creating our own html document for the news
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/news?artist="""



import os
from os import path
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
import DataModels as models


""" This class handles news requests"""
class NewsHandler(webapp.RequestHandler):
    def get(self, artist):
# Use GetArtistNews method to obtain news data for given artist
        name = self.request.get("artist")
        html = None
        if name:
            html = memcache.get(name + ' News')
            if html is None:
                newsData = models.GetArtistNews(name)
        else:
            newsData = {'status' : {'error' : 'artist unknown'}}

        if html is None:
            if newsData['status']['error'] == 'The echonest API call timed out':
                context = {'error' : 'Sorry, The echonest API call timed out'}
                tmpl = path.join(path.dirname(__file__), 'news.html')
                html = render(tmpl, context)
            elif newsData['status']['error'] == 'artist not found':
                context = {'error' : 'Whoa!  Not much buzz about this artist.\nMaybe you should create some!\nwww.tumblr.com'}
                tmpl = path.join(path.dirname(__file__), 'news.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            elif newsData['status']['error'] == 'artist unknown':
                context = {'error' : 'artist unknown'}
                tmpl = path.join(path.dirname(__file__), 'news.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            elif newsData['stories'] == []:
                context = {'error' : 'Whoa!  Not much buzz about this artist.\nMaybe you should create some!\nwww.tumblr.com'}
                tmpl = path.join(path.dirname(__file__), 'news.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            else:
                newsItems = newsData['stories']
                context = {'newsItems' : newsItems}
                tmpl = path.join(path.dirname(__file__), 'news.html')
                html = render(tmpl, context)
                SetNewsMemcache(name, html)
                self.response.out.write(html)
        else:
            self.response.out.write(html)
""" --- """

def SetNewsMemcache(artistName, newsHTML):
    data = memcache.get(artistName + ' News')
    if data is not None:
        memcache.set(artistName + ' News', newsHTML, 10800)
    else:
        memcache.add(artistName + ' News', newsHTML, 10800)
        

""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/news(.*)', NewsHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
