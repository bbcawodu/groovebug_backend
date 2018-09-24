""" This Handler is responsible for making the API calls to echonest, parsing the
    json data for a given artist, creating our own html document for artist bio
    using the data, and returning it when queried using our internal API
    the wrapper for news will be
    http://backendgroovebug.appspot.com/v1/bio?artist="""



import os
from os import path
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']

    
from google.appengine.ext import webapp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
import DataModels as models



""" Class that handles biography requests"""
class ImgAttHandler(webapp.RequestHandler):
    def get(self, imgid):
## Use GetArtistMusic method to obtain json data for the given artist
        imgid = self.request.get("imgid")
        context = {}
        context['takedown'] = ''
        if imgid:
            if imgid == 'noimage':
                context['source'] = 'http://' + str(hostUrl) + '/htmlimages/groovebugicon.png'
                context['sourcepage'] = 'http://groovebug.com'
                context['sourcepagetext'] = 'groovebug.com'
                context['directlink'] = ''
                context['directlinktext'] = ''
                context['attribution'] = 'n/a'
            else:
                imgRec = models.ArtistImages.get(imgid)
                if imgRec:
                    context = {}
                    context['source'] = imgRec.artistThmbUrl
                    if imgRec.artistOrigImgUrl == 'Manually Replaced' or imgRec.artistOrigImgUrl == 'Manually Added':
                        context['sourcepage'] = 'http://groovebug.com'
                        context['sourcepagetext'] = 'groovebug.com'
                        context['directlink'] = imgRec.artistImgUrl
                        context['directlinktext'] = imgRec.artistImgUrl[:20] + '...'
                        context['attribution'] = 'n/a'
                    else:
                        if imgRec.artistImgLicense:
                            imgLic = imgRec.artistImgLicense
                            context['sourcepagetext'] = 'Missing'
                            if imgLic.has_key('url'):
                                if imgLic['url'] != "":
                                    context['sourcepage'] = imgLic['url']
                                    context['sourcepagetext'] = imgLic['url'][:20] + '...'

                            context['attribution'] = 'n/a'
                            if imgLic.has_key('attribution'):
                                if imgLic['url'] != "":
                                    context['attribution'] = imgLic['attribution']
                                    
                            context['takedown'] = 'Are you a party pooper? <a href="http://groovebug.com/dmca-notice-takedown-procedure">DMCA Takedown</a>'
                        else:
                            #context['sourcepage'] = ''
                            context['sourcepagetext'] = 'Missing'
                            context['attribution'] = 'n/a'

                        context['directlink'] = imgRec.artistOrigImgUrl
                        context['directlinktext'] = imgRec.artistOrigImgUrl[:20] + '...'
                else:
                    context['error'] = 'Image Record Not Found'
        else:
            context['error'] = 'No Image Key'
                

## If the echonest API request timed out, display error message
        if context == {}:
            context = {'error' : 'Sorry, there was an unknown error'}
            tmpl = path.join(path.dirname(__file__), 'imgatt.html')
            html = render(tmpl, context)
            self.response.out.write(html)
# Otherwise, display error message
        else:
            tmpl = path.join(path.dirname(__file__), 'imgatt.html')
            html = render(tmpl, context)
            self.response.out.write(html)
""" --- """




""" Main function which handles url mapping"""
application = webapp.WSGIApplication([('/v1/imgatt(.*)', ImgAttHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
