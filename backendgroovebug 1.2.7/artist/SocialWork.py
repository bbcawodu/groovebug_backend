""" This Handler is responsible for making the API calls, parsing the
    json data for a given artist, creating our own html document for social media info
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/artist/socialwork?artist="""



import os
from os import path
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']

if str(hostUrl) == 'backendgroovebug.appspot.com':
    APIKEY = '269A92REW5YH3KNZW'
elif str(hostUrl) == 'testgroovebug.appspot.com':
    APIKEY = 'GN7EUP6EYOFTT75NN'
else:
    APIKEY = 'GN7EUP6EYOFTT75NN'
    
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
import urllib, logging
import DataModels as models
logging.getLogger().setLevel(logging.DEBUG)


""" This class handles news requests"""
class SocialWorkHandler(webapp.RequestHandler):
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
        if name:
            socialFiles = models.ArtistSocial.gql("WHERE artistName = :1 LIMIT 1", artistEnc).fetch(1)
            if len(socialFiles) > 0:
                socialData = {'status' : {'error' : 0}}
                socialFile = socialFiles[0]
            else:
                socialFile = None
                socialData = {'status' : {'error' : 'artist not found'}}
        else:
            socialData = {'status' : {'error' : ''}}
            socialFile = None

        if socialData['status']['error'] == 'The echonest API call timed out':
            context = {'error' : 'Sorry, The echonest API call timed out'}
            tmpl = path.join(path.dirname(__file__), 'socialwork.html')
            html = render(tmpl, context)
        elif socialData['status']['error'] == 'artist not found':
            actionMsg = 'Social media info was not found for this artist'
            context = {'error' : actionMsg, 'artist' : name, 'artistEnc' : artistEnc}
            tmpl = path.join(path.dirname(__file__), 'socialwork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
        elif socialData['status']['error'] == 'artist unknown':
            context = {'error' : 'artist unknown'}
            tmpl = path.join(path.dirname(__file__), 'socialwork.html')
            html = render(tmpl, context)
            self.response.out.write(html)
        else:
            if actionMsg == '':
                context = {'social' : socialFile, 'artist' : name, 'artistEnc' : artistEnc}
            else:
                context = {'error' : actionMsg, 'social' : socialFile, 'artist' : name, 'artistEnc' : artistEnc}
            tmpl = path.join(path.dirname(__file__), 'socialwork.html')
            html = render(tmpl, context)
            self.response.out.write(html)

""" --- """



class SocialWorkRedirect(webapp.RequestHandler):
    """Handler for News replacing and deleting."""
      
    def post(self, artist):
        #user = users.get_current_user()
        #userName = user.nickname()
        #logoutUrl = users.create_logout_url('/artist/newswork')

        actionMsg = ''

        if self.request.get('getSocial'):
            artist = self.request.get('getSocial')
            artistEnc = artist.encode('utf-8')
            if artist:
                if artist != '':
                    socialFile = models.getArtistSocial(artist)
                    logging.info('social file: ' + str(socialFile))
                    if socialFile:
                        logging.info('the socialFile compare worked')
                        if not socialFile is None:
                            logging.info('the socialFile is not none compare worked')
                        else:
                            actionMsg = 'Could not get social media info'
                    else:
                        actionMsg = 'Could not get social media info'
                else:
                    actionMsg = 'There is no artist name'
            else:
                actionMsg = 'There is no artist name'

            if actionMsg == '':
                self.redirect('/artist/socialwork?artist=' + artistEnc)
            else:
                self.redirect('/artist/socialwork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
                
        elif self.request.get('updateSocial'):
            artist = self.request.get('artistName')
            artistEnc = self.request.get('artistEnc')
            socialFile = models.ArtistSocial.get_or_insert(key_name = str(artistEnc), artistName = artistEnc)
            if socialFile:
                socialFile.website = self.request.get('website')
                socialFile.twitter = self.request.get('twitter')
                socialFile.facebook = self.request.get('facebook')
                socialFile.myspace = self.request.get('myspace')
                socialFile.soundcloud = self.request.get('soundcloud')
                socialFile.wikipedia = self.request.get('wikipedia')
                socialFile.youtube = self.request.get('youtube')
                socialFile.lastfm = self.request.get('lastfm')
                socialFile.tumblr = self.request.get('tumblr')
                socialFile.purevolume = self.request.get('purevolume')
                socialFile.put()
                actionMsg = artist + ' Social Info Updated'
            else:
                actionMsg = artist + ' Social File Not Found'
            self.redirect('/artist/socialwork?artist=' + artistEnc + '&actionMsg=' + urllib.quote(actionMsg))
        else:
            artist = self.request.get('artistName')
            artistEnc = self.request.get('artistEnc')
            self.redirect('/artist/socialwork?artist=' + artistEnc)
            
        

""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist/socialwork(.*)', SocialWorkHandler),
                                      ('/artist/socialredirect(.*)', SocialWorkRedirect),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
