import os
from os import path
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
import DataModels as models



class NoBuyPageHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        context = {'url' : self.request.url}
        tmpl = path.join(path.dirname(__file__), 'missingbuy.html')
        html = render(tmpl, context)
        self.response.out.write(html)



""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/artist/missingbuy*', NoBuyPageHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
