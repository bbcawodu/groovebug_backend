""" This Handler is responsible for cleaning out the datastore of Similar
    Artist entries that are over a week old"""



import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import DataModels as models
import urllib, logging, datetime
logging.getLogger().setLevel(logging.DEBUG)

    
""" Class that handles cleaning of the datastore"""
class CorrectionHandler(webapp.RequestHandler):
    def get(self):
        currentDateTime = datetime.datetime.utcnow()
        artistEntries = models.SimilarArtists.all()
        for artistEntry in artistEntries:
            dateAdded = artistEntry.date_added
            timeDifference = currentDateTime - dateAdded
            if timeDifference.days >= 7:
                self.response.out.write(artistEntry.artist_name + ' deleted <br/>')
                artistEntry.delete()
            else:
                self.response.out.write(artistEntry.artist_name + ' NOT deleted <br/>')
        
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/similarartistcrawler', CorrectionHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
