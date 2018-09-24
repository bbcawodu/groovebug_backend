""" This Handler is responsible for making the API calls to echonest, parsing the
    json data for a given artist, creating our own html document for artist bio
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/bio?artist="""



import os
from os import path
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
import DataModels as models



""" Class that handles biography requests"""
class BioHandler(webapp.RequestHandler):
    def get(self, artist):
## Use GetArtistBio method to obtain json data for the given artist
        name = self.request.get("artist")
        html = None
        if name:
            html = memcache.get(name + ' Bio')
            if html is None:
                bioData = models.GetArtistBio(name)
        else:
            bioData = {'status' : {'error' : 'artist unkown'}}
        
## If the echonest API request timed out, display error message
        if html is None:
            if bioData['status']['error'] == 'The echonest API request timed out':
                context = {'error' : 'Sorry, the echonest API request timed out'}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                self.response.out.write(html)
    # If the artist wasnt found, display error message
            elif bioData['status']['error'] == 'artist not found':
                context = {'error' : 'Sorry, artist not found in biography database'}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                self.response.out.write(html)
    # If the artist wasnt found (because it was blank), display error message
            elif bioData['status']['error'] == 'artist unkown':
                context = {'error' : 'Sorry, artist unkown'}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                self.response.out.write(html)
    # If there is a Groovebug Content, display it
            elif bioData['bios'].has_key('Groovebug Content'):
                bio = {}
                bio['source'] = bioData['bios']['Groovebug Content']['source']
                bio['text'] = bioData['bios']['Groovebug Content']['text']
                bio['url'] = bioData['bios']['Groovebug Content']['url']
                context = {'bio' : bio}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                SetBioMemcache(name, html)
                self.response.out.write(html)
    # If there is a wikipedia bio, display it
            elif bioData['bios'].has_key('wikipedia'):
                bio = {}
                bio['source'] = 'Wikipedia'
                bio['text'] = models.ChkTxtEnc(bioData['bios']['wikipedia']['generalBio'])
                bio['url'] = bioData['bios']['wikipedia']['url']
                context = {'bio' : bio}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                SetBioMemcache(name, html)
                self.response.out.write(html)
    # If there is a Last.fm bio, display it
            elif bioData['bios'].has_key('last.fm'):
                bio = {}
                bio['source'] = 'Last.fm'
                bio['text'] = models.ChkTxtEnc(bioData['bios']['last.fm']['text'])
                bio['url'] = bioData['bios']['last.fm']['url']
                context = {'bio' : bio}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                SetBioMemcache(name, html)
                self.response.out.write(html)
    # Otherwise, display error message
            else:
                context = {'error' : 'This artist needs some help. Go to wikipedia and get their bio started!',
                           'link': 'http://en.wikipedia.org/w/index.php?title=Special:UserLogin&returnto=Main_Page&campaign=ACP2'}
                tmpl = path.join(path.dirname(__file__), 'bio.html')
                html = render(tmpl, context)
                self.response.out.write(html)
        else:
            self.response.out.write(html)

""" --- """

def SetBioMemcache(artistName, bioHTML):
    data = memcache.get(artistName + ' Bio')
    if data is not None:
        memcache.set(artistName + ' Bio', bioHTML, 604800)
    else:
        memcache.add(artistName + ' Bio', bioHTML, 604800)


""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/bio(.*)', BioHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
