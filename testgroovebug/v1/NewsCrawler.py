""" This Handler is responsible for cleaning out the datastore of Similar
    Artist entries that are over a week old"""



import os
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from django.utils import simplejson as json
import DataModels as models
import echonestlib as echonest
import urllib, logging, datetime
logging.getLogger().setLevel(logging.DEBUG)

    
""" Class that handles cleaning of the datastore"""
class CorrectionHandler(webapp.RequestHandler):
    def get(self):
        logging.info('Start')
        artistsToBeUpdated = []
        outdatedEntryKeys = []
        oldestAllowedEntry = datetime.datetime.utcnow() - datetime.timedelta(seconds=10800)
        
        logging.info('Getting keys for outdated echonest news entries')
        outdatedEntryKeysQuery = db.GqlQuery("SELECT __key__ FROM EchonestNews " +
                                             "WHERE date_added <= :oldestTime " +
                                             "LIMIT 1000",
                                             oldestTime = oldestAllowedEntry)
        for correctionKey in outdatedEntryKeysQuery:
            outdatedEntryKeys.append(correctionKey)

        if outdatedEntryKeys != []:
            logging.info('Getting entries for ' + str(len(outdatedEntryKeys)) + ' outdated echonest news entries')
            artistEntries = models.EchonestNews.get(outdatedEntryKeys)
            
            for index, artistEntry in enumerate(artistEntries):
                artistsToBeUpdated.append(artistEntry.artist_name)
                memcache.delete('echonestNewsCache' + artistEntry.artist_name)
                artistEntry.delete()
                if len(artistsToBeUpdated) >= 200 or index+1 == len(artistEntries):
                    logging.info(str(len(artistsToBeUpdated)) + ' artists about to be updated')
                    updatedArtists = echonest.GetNewsForArtists(artistsToBeUpdated, deadline=20, maxFails = 3*len(artistsToBeUpdated))
                    artistsToBeUpdated = []
        else:
            logging.info('No outdated echonest news entries found')
        logging.info('FINISH') 
""" --- """



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/newscrawler', CorrectionHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
