""" This Handler is responsible for making the API calls, parsing the
    json data for a given artist, creating our own html document for the news
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/news?artist="""



from os import path
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
import urllib
import DataModels as models


""" This class handles news requests"""
class NewsWorkHandler(webapp.RequestHandler):
    def get(self, artist):
# Use GetArtistNews method to obtain news data for given artist
        name = self.request.get("artist")
        artistEnc = name.encode('utf-8')
        artistEnc = urllib.quote_plus(artistEnc)
        if self.request.get("actionMsg"):
            actionMsg = self.request.get("actionMsg")
        else:
            actionMsg = ''
            
        html = None
        #if name:
        #    html = memcache.get(name + ' News')
        #    if html is None:
        #        newsData = models.GetArtistNews(name)
        #else:
        #    newsData = {'status' : {'error' : 'artist unknown'}}
        if name:
            newsData = models.GetArtistNews(name, blink = True, edit=True)
        else:
            newsData = {'status' : {'error' : ''}}
            newsData['stories'] = []

        if html is None:
            #newsData = models.GetArtistNews(self.request.get("artist"))
            if newsData['status']['error'] == 'The echonest API call timed out':
                context = {'error' : 'Sorry, The echonest API call timed out'}
                tmpl = path.join(path.dirname(__file__), 'newswork.html')
                html = render(tmpl, context)
            elif newsData['status']['error'] == 'artist not found':
                actionMsg = 'Whoa!  Not much buzz about this artist.\nMaybe you should create some!\nwww.tumblr.com'
                context = {'error' : actionMsg, 'artist' : name, 'artistEnc' : artistEnc}
                tmpl = path.join(path.dirname(__file__), 'newswork.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            elif newsData['status']['error'] == 'artist unknown':
                context = {'error' : 'artist unknown'}
                tmpl = path.join(path.dirname(__file__), 'newswork.html')
                html = render(tmpl, context)
                self.response.out.write(html)
            else:
                newsItems = newsData['stories']
                if actionMsg == '':
                    context = {'newsItems' : newsItems, 'artist' : name, 'artistEnc' : artistEnc}
                else:
                    context = {'error' : actionMsg, 'newsItems' : newsItems, 'artist' : name, 'artistEnc' : artistEnc}
                tmpl = path.join(path.dirname(__file__), 'newswork.html')
                html = render(tmpl, context)
                #SetNewsMemcache(name, html)
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


class NewsWorkRedirect(webapp.RequestHandler):
    """Handler for News replacing and deleting."""
      
    def post(self, artist):
        #user = users.get_current_user()
        #userName = user.nickname()
        #logoutUrl = users.create_logout_url('/artist/newswork')

        #artist = self.request.get('artistName')
        artistEnc = self.request.get('artistEnc')
        actionMsg = ''

        if self.request.get('addNews'):
            if artistEnc != '':
                if not self.request.get('newstitle'):
                    actionMsg = 'You Need A Title To Add A News Story'
                else:
                    nTitle = self.request.get('newstitle')
                    nTitle = nTitle.strip()
                    if nTitle == '':
                        actionMsg = 'You Need A Title To Add A News Story'
                    else:
                        if not self.request.get('newsdate'):
                            actionMsg = 'You Need A Date To Add A News Story'
                        else:
                            nDate = self.request.get('newsdate')
                            nDate = nDate.strip()
                            if nDate == '':
                                actionMsg = 'You Need A Date To Add A News Story'
                            else:
                                if not self.request.get('newssource'):
                                    actionMsg = 'You Need A Source To Add A News Story'
                                else:
                                    nSource = self.request.get('newssource')
                                    nSource = nSource.strip()
                                    if nSource == '':
                                        actionMsg = 'You Need A Source To Add A News Story'
                                    else:
                                        if not self.request.get('newsTxt'):
                                            actionMsg = 'You Need A Summary To Add A News Story'
                                        else:
                                            nSummary = self.request.get('newsTxt')
                                            nSummary = nSummary.strip()
                                            if nSummary == '':
                                                actionMsg = 'You Need A Summary To Add A News Story'
                                            else:
                                                if not self.request.get('newsurl'):
                                                    actionMsg = 'You Need A URL To Add A News Story'
                                                else:
                                                    nUrl = self.request.get('newsurl')
                                                    nUrl = nUrl.strip()
                                                    if nUrl == '':
                                                        actionMsg = 'You Need A URL To Add A News Story'
            else:
                actionMsg = 'There is no artist name'

            if actionMsg == '':
                try:
                    newsRec = models.PromotedNews(artistName = artistEnc, title = nTitle)
                    if newsRec:
                        newsRec.date = nDate
                        newsRec.articleSource  = nSource
                        newsRec.apiSource  = 'Groovebug'
                        newsRec.summary  = nSummary
                        newsRec.url  = nUrl
                        newsRec.put()
                        actionMsg = 'News Story Added'
                    else:
                        actionMsg = 'Could Not Find News DB entry'
                except Exception, error:
                    actionMsg = error
                    self.response.out.write(actionMsg)
                    return 'ok'
                    
            self.redirect('/artist/newswork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
        elif self.request.get('deleteNews'):
            itemKey = self.request.get('deleteNews')
            #nTitle = self.request.get('title')
            delFile = db.get(itemKey)
            nTitle = delFile.title
            delFile.delete()
            actionMsg = nTitle + ' Deleted'
            self.redirect('/artist/newswork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
        elif self.request.get('excludeNews'):
            exclUrl = self.request.get('excludeNews')
            wrkFile = models.ArtistWork.get_or_insert(key_name = str(artistEnc), artistName = artistEnc)
            exclList = []
            exclUrl = exclUrl.strip().lower()
            if wrkFile:
                if wrkFile.newsToExclude:
                    if not wrkFile.newsToExclude is None:
                        exclList = wrkFile.newsToExclude
                
                if exclUrl not in exclList:
                    exclList.append(exclUrl)
                wrkFile.newsToExclude = exclList
                wrkFile.put()
                actionMsg = 'Item Excluded!!!'
            else:
                actionMsg = 'Problem Getting Exlusion List'
                
            self.redirect('/artist/newswork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
        else:
            self.redirect('/artist/newswork?artist=' + artistEnc)
            
        

""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist/newswork(.*)', NewsWorkHandler),
                                      ('/artist/newsredirect(.*)', NewsWorkRedirect),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
