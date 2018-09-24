""" This Handler is responsible adding composite data to the
    backend server.
    the URL is
    http://backendgroovebug.appspot.com/v1/composite-manager"""



from __future__ import with_statement
import os
from os import path
from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import util
from google.appengine.api import users, files, images
from google.appengine.ext.webapp import blobstore_handlers
from django.utils import simplejson as json
import DataModels as models
import urllib2, urllib, re
if os.environ.get('HTTP_HOST'):
    hostUrl = os.environ['HTTP_HOST']
else:
    hostUrl = os.environ['SERVER_NAME']



""" This method removes HTML or XML character references and entities from a text
    string, and returns the plain text, as a Unicode string, if necessary.
    got from:  http://effbot.org/zone/re-sub.htm#unescape-html"""
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
""" --- """


          
""" Class that handles composite manager homepage"""
class CompositeManagerHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/composite-manager')
        
        compositePages = models.CompositePage.all()
        compositeList = []
        for compositePage in compositePages:
            page = {}
            page['title'] = compositePage.title
            page['compositeType'] = compositePage.compositeType
            if compositePage.status:
                page['status'] = compositePage.status
            else:
                page['status'] = 'Normal'
            pagekey = compositePage.key()
            page['compPageId'] = pagekey.id()
            if compositePage.contentType == 'userInput':
                page['url'] = 'http://' + str(hostUrl) + '/v1/compositehtml?id=' + str(page['compPageId'])
            else:
                page['url'] = compositePage.content
            compositeList.append(page)
##            compositePage.delete()
##            artistListJsonData = []
##            artistList = compositePage.artistList
##            for artist in artistList:
##                artistDictEntry = {}
##                artistDictEntry['name'] = artist.encode('utf-8')
##                artistDictEntry['magazine'] = "http://backendgroovebug.appspot.com/v1/magazine?artist=" + urllib.quote_plus(artistDictEntry['name'])
##                artistListJsonData.append(artistDictEntry)
##            artistListJson = json.dumps(artistListJsonData, separators=(',',':'))
##            artistListJson = artistListJson.encode('utf-8')
##            compositePage.artistListJson = artistListJson
##            compositePage.put()

        context = {'title' : 'Composite Pages List',
                   'user' : userName,
                   'logoutUrl' : logoutUrl,
                   'compositeList' : compositeList,}
        tmpl = path.join(path.dirname(__file__), 'compositeManagerHome.html')
        html = render(tmpl, context)
        self.response.out.write(html)
""" --- """



""" Class that handles the new composite page"""
class NewCompositeHandler(webapp.RequestHandler):
    def post(self):
        logoutUrl = users.create_logout_url('/artist/composite-manager')
        contentTypeOptions = ['HTML', 'userInput']
        compPage = {}
        compositeTypeOptionString = '<input type=text name="compositeType" value="Artists" maxlength="1000">'
        compPage['compositeType'] = compositeTypeOptionString
        
        statusOptions = ['Normal', 'New']
        statusOptionString = '<select name="status">'
        for option in statusOptions:
            statusOptionString = statusOptionString + '<option value="' + option + '"'
            statusOptionString = statusOptionString + '>'
            statusOptionString = statusOptionString + option + '</option>'
        statusOptionString = statusOptionString + '</select>'
        compPage['status'] = statusOptionString

        contentTypeOptions = ['HTML', 'userInput']
        contentTypeOptionsString = "<select name='contentType' onchange='s(this)' style='font-size : 20px;'>"
        
        for option in contentTypeOptions:
            contentTypeOptionsString = contentTypeOptionsString + '<option value="'
            contentTypeOptionsString = contentTypeOptionsString + option + '"'
            contentTypeOptionsString = contentTypeOptionsString + '>'
            if option == 'userInput':
                contentTypeOptionsString = contentTypeOptionsString + 'Image and Summary'
            else:
                contentTypeOptionsString = contentTypeOptionsString + option
            contentTypeOptionsString = contentTypeOptionsString+ '</option>'
            
        contentTypeOptionsString = contentTypeOptionsString + '</select>'
        compPage['contentType'] = contentTypeOptionsString
        context = {'logoutUrl' : logoutUrl,
                   'compPage' : compPage,
                   'title' : 'New Composite Page'}
        tmpl = path.join(path.dirname(__file__), 'compositeManager.html')
        html = render(tmpl, context)
        self.response.out.write(html)
""" --- """



""" Class that handles form data submission"""
class RedirectCompositeHandler(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/composite-manager')

        title = self.request.get('title')
        title = title.encode('utf-8')
        artistText = self.request.get('artistList')
        artistText = unescape(artistText)
        artistList = re.findall('[^\n|\r]+', artistText)
        compositeType = self.request.get('compositeType')
        compositeType = compositeType.encode('utf-8')
        status = self.request.get('status')
        status = status.encode('utf-8')
        contentType = self.request.get('contentType')
        contentType = contentType.encode('utf-8')
        if contentType == 'HTML':
            if self.request.get('content'):
                content = self.request.get('content')
                content = content.encode('utf-8')
            else:
                content = 'http://blog.groovebug.com/'
        if contentType == 'userInput':
            summary = self.request.get('summary')
            summary = unescape(summary)
            summaryUrl = self.request.get('summaryurl')
            summaryUrl = summaryUrl.encode('utf-8')

        compPage = {}
        compPage['title'] = title

        compositeTypeOptionString = '<input type=text name="compositeType"'
        if compositeType:
            compositeTypeOptionString =  compositeTypeOptionString + ' value="' + contentType + '"'
        compositeTypeOptionString =  compositeTypeOptionString + ' maxlength="1000">'
        compPage['compositeType'] = compositeTypeOptionString
        #compPage['compositeType'] = compositeType

        statusOptions = ['Normal', 'New']
        statusOptionString = '<select name="status">'
        for option in statusOptions:
            statusOptionString = statusOptionString + '<option value="' + option + '"'
            if status:
                if status == option:
                    statusOptionString = statusOptionString + ' SELECTED'
            
            statusOptionString = statusOptionString + '>'
            statusOptionString = statusOptionString + option + '</option>'
        statusOptionString = statusOptionString + '</select>'
        compPage['status'] = statusOptionString
        #compPage['status'] = status
        
        compPage['artistList'] = artistText
        if self.request.get('artistListErrors') != '':
            compPage['artistListErrors'] = self.request.get('artistListErrors')

        contentTypeOptions = ['HTML', 'userInput']
        contentTypeOptionsString = "<select name='contentType' onchange='s(this)' style='font-size : 20px;'>"
        if contentType:
            if contentType not in contentTypeOptions:
                contentTypeOptionsString = contentTypeOptionsString + '<option value="Select" SELECTED>Select</option>'
        else:
            contentTypeOptionsString = contentTypeOptionsString + '<option value="Select" SELECTED>Select</option>'
        
        for option in contentTypeOptions:
            contentTypeOptionsString = contentTypeOptionsString + '<option value="'
            contentTypeOptionsString = contentTypeOptionsString + option + '"'
            if contentType:
                if contentType == option:
                    contentTypeOptionsString = contentTypeOptionsString + ' SELECTED'
            contentTypeOptionsString = contentTypeOptionsString + '>'
            if option == 'userInput':
                contentTypeOptionsString = contentTypeOptionsString + 'Image and Summary'
            else:
                contentTypeOptionsString = contentTypeOptionsString + option
            contentTypeOptionsString = contentTypeOptionsString+ '</option>'
            
        contentTypeOptionsString = contentTypeOptionsString + '</select>'
        compPage['contentType'] = contentTypeOptionsString

        #compPage['contentType'] = contentType
        if contentType == 'HTML':
            compPage['content'] = content
        if contentType == 'userInput':
            compPage['summary'] = summary
            compPage['summaryUrl'] = summaryUrl
            if self.request.get('graphicurl') != '' or self.request.get('graphicurl') != 'N/A':
                compPage['graphicUrl'] = self.request.get('graphicurl')
        if self.request.get('thumbnailurl') != '' or self.request.get('thumbnailurl') != 'N/A':
                compPage['thumbnailUrl'] = self.request.get('thumbnailurl')
            
        if self.request.get('verify') == 'yes':
            searchBase = 'http://developer.echonest.com/api/v4/artist/search?api_key=269A92REW5YH3KNZW&'
            searchArgs = {'format' : 'json',
                          'results' : '1',
                          'fuzzy_match' : 'false',}
            searchHelper = models.UrlFetchHelper(searchBase, searchArgs)
            
            correctedArtists = []
            errorArtists = []
            for artist in artistList:
                artist = artist.encode('utf-8')
                searchJson = searchHelper.MakeSyncJsonFetch('name', artist)
                if searchJson == [] or searchJson['response']['artists'] == []:
                    errorArtists.append(artist)
                else:
                    correctedArtist = searchJson['response']['artists'][0]['name']
                    correctedArtists.append(correctedArtist)
                    
            correctedString = ""
            if self.request.get('artistListErrors'):
                errorString = self.request.get('artistListErrors')
                errorString = unescape(errorString)
                errorString = errorString.encode('utf-8')
            else:
                errorString = ""
                
            if not errorArtists == []:
                for artist in errorArtists:
                    errorString = errorString + artist + "\n"
            if not correctedArtists == []:
                for artist in correctedArtists:
                        correctedString = correctedString + artist + "\n"
            
            compPage['artistList'] = correctedString
            compPage['artistListErrors'] = errorString
            
            if self.request.get('hasid') == 'yes':
                compPage['compPageId'] = self.request.get('compositeid')
                urlTitle = 'Edit Composite Page'
            else:
                urlTitle = 'New Composite Page'
            tmpl = path.join(path.dirname(__file__), 'compositeManager.html')
            context = {'title' : urlTitle ,
                       'user' : userName,
                       'logoutUrl' : logoutUrl,
                       'compPage' : compPage,}    
            html = render(tmpl, context)
            self.response.out.write(html)

        elif artistList == []:
            urlTitle = 'AAMIR! artist list is empty'
            tmpl = path.join(path.dirname(__file__), 'compositeManager.html')
            context = {'title' : urlTitle,
                       'user' : userName,
                       'logoutUrl' : logoutUrl,
                       'compPage' : compPage,}    
            html = render(tmpl, context)
            self.response.out.write(html)
            
        else:
            artistListJsonData = []
            for artist in artistList:
                    artistDictEntry = {}
                    artistDictEntry['name'] = artist
                    artistDictEntry['magazine'] = 'http://' + str(hostUrl) + '/v1/magazine?artist=' + urllib.quote_plus(artistDictEntry['name'].encode('utf-8'))
                    artistListJsonData.append(artistDictEntry)
            artistListJson = json.dumps(artistListJsonData, separators=(',',':'))
            artistListJson = artistListJson.encode('utf-8')

            if self.request.get('deleteThumbnail') == 'yes':
                compPageId = self.request.get('compositeid')
                compPage['compPageId'] = compPageId
                compPageId = int(compPageId)
                compositePage = models.CompositePage.get_by_id(compPageId)
                
                if compositePage.thumbnailUrl != 'N/A':
                    if compositePage.thumbnailBlobKey != 'N/A':
                        blobstore.delete(compositePage.thumbnailBlobKey)
                    elif compositePage.thumbnail != None:
                        blobstore.delete(self.request.get('compositeid'))
                    compositePage.thumbnailUrl = 'N/A'
                    compPage['thumbnailUrl'] = None
                    compositePage.thumbnailBlobKey = 'N/A'
                    if compositePage.graphicBlobKey != 'N/A':
                        compPage['graphicUrl'] = compositePage.graphicUrl
                compositePage.put()
                
                context = {'title' : 'Thumbnail Deleted!!!  Edit Composite Page',
                           'user' : userName,
                           'logoutUrl' : logoutUrl,
                           'compPage' : compPage,}
                tmpl = path.join(path.dirname(__file__), 'compositeManager.html')
                html = render(tmpl, context)
                self.response.out.write(html)
                
            elif self.request.get('deleteGraphic') == 'yes':
                compPageId = self.request.get('compositeid')
                compPage['compPageId'] = compPageId
                compPageId = int(compPageId)
                compositePage = models.CompositePage.get_by_id(compPageId)
                
                if compositePage.graphicUrl != 'N/A':
                    if compositePage.graphicBlobKey != 'N/A':
                        blobstore.delete(compositePage.graphicBlobKey)
                    compositePage.graphicUrl = 'N/A'
                    compPage['graphicUrl'] = None
                    compositePage.graphicBlobKey = 'N/A'
                    if compositePage.thumbnailBlobKey != 'N/A':
                        compPage['thumbnailUrl'] = compositePage.thumbnailUrl
                compositePage.put()
                    
                context = {'title' : 'Graphic Deleted!!!  Edit Composite Page',
                           'user' : userName,
                           'logoutUrl' : logoutUrl,
                           'compPage' : compPage,}
                tmpl = path.join(path.dirname(__file__), 'compositeManager.html')
                html = render(tmpl, context)
                self.response.out.write(html)
                
            elif self.request.get('hasid') == 'yes':
                compPageId = self.request.get('compositeid')
                compPageId = int(compPageId)
                compositePage = models.CompositePage.get_by_id(compPageId)
                        
                if not self.request.get("thumbnail") == '':
                    thumbnail = self.request.get("thumbnail")
                    thumbnailImg = models.db.Blob(thumbnail)
                    blobstoreThumbnail = files.blobstore.create(mime_type='image/jpeg')
                    with files.open(blobstoreThumbnail, 'a') as f:
                        f.write(thumbnailImg)
                    files.finalize(blobstoreThumbnail)
                    thumbnailBlobKey = files.blobstore.get_blob_key(blobstoreThumbnail)
                    compositePage.thumbnailBlobKey = str(thumbnailBlobKey)
                    compositePage.thumbnailUrl = images.get_serving_url(thumbnailBlobKey)
                compositePage.artistListJson = artistListJson
                compositePage.artistList = artistList
                compositePage.compositeType = compositeType
                compositePage.status = status
                compositePage.title = title
                compositePage.compositeUrl = 'http://' + str(hostUrl) + '/v1/composite?name=' + urllib.quote_plus(title)
                compositePage.contentType = contentType
                if contentType == 'HTML':
                    compositePage.content = content
                if contentType == 'userInput':
                    compositePage.summary = summary
                    compositePage.summaryUrl = summaryUrl
                    if not self.request.get("graphic") == '':
                        graphic = self.request.get("graphic")
                        graphicImg = models.db.Blob(graphic)
                        blobstoreGraphic = files.blobstore.create(mime_type='image/jpeg')
                        with files.open(blobstoreGraphic, 'a') as f:
                            f.write(graphicImg)
                        files.finalize(blobstoreGraphic)
                        graphicBlobKey = files.blobstore.get_blob_key(blobstoreGraphic)
                        compositePage.graphicBlobKey = str(graphicBlobKey)
                        compositePage.graphicUrl = images.get_serving_url(graphicBlobKey)
                compositePage.put()
                self.redirect('/artist/composite-manager')
                
            else:
                compositePage = models.CompositePage(artistList = artistList, key_name=None)

                if not self.request.get("thumbnail") == '':
                    thumbnail = self.request.get("thumbnail")
                    thumbnailImg = models.db.Blob(thumbnail)
                    blobstoreThumbnail = files.blobstore.create(mime_type='image/jpeg')
                    with files.open(blobstoreThumbnail, 'a') as f:
                        f.write(thumbnailImg)
                    files.finalize(blobstoreThumbnail)
                    thumbnailBlobKey = files.blobstore.get_blob_key(blobstoreThumbnail)
                    compositePage.thumbnailBlobKey = str(thumbnailBlobKey)
                    compositePage.thumbnailUrl = images.get_serving_url(thumbnailBlobKey)
                else:
                    compositePage.thumbnailBlobKey = 'N/A'
                    compositePage.thumbnailUrl = 'http://' + str(hostUrl) + '/v1/static/default_black_tile_200x200.png'
                compositePage.artistListJson = artistListJson
                compositePage.artistList = artistList
                compositePage.compositeType = compositeType
                compositePage.status = status
                compositePage.title = title
                compositePage.compositeUrl = 'http://' + str(hostUrl) + '/v1/composite?name=' + urllib.quote_plus(title)
                compositePage.contentType = contentType
                if contentType == 'HTML':
                    compositePage.content = content
                if contentType == 'userInput':
                    compositePage.summary = summary
                    compositePage.summaryUrl = summaryUrl
                    if not self.request.get("graphic") == '':
                        graphic = self.request.get("graphic")
                        graphicImg = models.db.Blob(graphic)
                        blobstoreGraphic = files.blobstore.create(mime_type='image/jpeg')
                        with files.open(blobstoreGraphic, 'a') as f:
                            f.write(graphicImg)
                        files.finalize(blobstoreGraphic)
                        graphicBlobKey = files.blobstore.get_blob_key(blobstoreGraphic)
                        compositePage.graphicBlobKey = str(graphicBlobKey)
                        compositePage.graphicUrl = images.get_serving_url(graphicBlobKey)
                    else:
                        compositePage.graphicBlobKey = 'N/A'
                        compositePage.graphicUrl = 'http://' + str(hostUrl) + '/v1/static/default_black_tile_600x200.png'
                compositePage.put()
                self.redirect('/artist/composite-manager')
""" --- """



        
""" Class that handles composite editor page"""
class EditCompositeHandler(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        userName = user.nickname()
        logoutUrl = users.create_logout_url('/artist/composite-manager')
        
        compPageId = self.request.get('compositeid')
        compPageId = int(compPageId)
        currentCompPage = models.CompositePage.get_by_id(compPageId)
        
        if currentCompPage is None:
            self.response.out.write(compPageId)
            
        else:
            if self.request.get('delete') == 'yes':
                currentCompPage.delete()
                self.redirect('/artist/composite-manager')

            else:
                compPage = {}

                compositeTypeOptionString = '<input type=text name="compositeType"'
                if currentCompPage.compositeType:
                    compositeTypeOptionString =  compositeTypeOptionString + ' value="' + currentCompPage.compositeType + '"'
                compositeTypeOptionString =  compositeTypeOptionString + ' maxlength="1000">'
                compPage['compositeType'] = compositeTypeOptionString
                
                statusOptions = ['Normal', 'New']
                statusOptionString = '<select name="status">'
                for option in statusOptions:
                    statusOptionString = statusOptionString + '<option value="' + option + '"'
                    if currentCompPage.status:
                        if currentCompPage.status == option:
                            statusOptionString = statusOptionString + ' SELECTED'
                    
                    statusOptionString = statusOptionString + '>'
                    statusOptionString = statusOptionString + option + '</option>'
                statusOptionString = statusOptionString + '</select>'
                compPage['status'] = statusOptionString
                    
                artistList = currentCompPage.artistList
                artistListString = ''
                for artist in artistList:
                    artistListString = artistListString + artist + '\n'
                compPage['artistList'] = artistListString
                compPage['title'] = currentCompPage.title

                contentTypeOptions = ['HTML', 'userInput']
                contentTypeOptionsString = "<select name='contentType' onchange='s(this)' style='font-size : 20px;'>"
                if currentCompPage.contentType:
                    if currentCompPage.contentType not in contentTypeOptions:
                        contentTypeOptionsString = contentTypeOptionsString + '<option value="Select" SELECTED>Select</option>'
                else:
                    contentTypeOptionsString = contentTypeOptionsString + '<option value="Select" SELECTED>Select</option>'
                
                for option in contentTypeOptions:
                    contentTypeOptionsString = contentTypeOptionsString + '<option value="'
                    contentTypeOptionsString = contentTypeOptionsString + option + '"'
                    if currentCompPage.contentType:
                        if currentCompPage.contentType == option:
                            contentTypeOptionsString = contentTypeOptionsString + ' SELECTED'
                    contentTypeOptionsString = contentTypeOptionsString + '>'
                    if option == 'userInput':
                        contentTypeOptionsString = contentTypeOptionsString + 'Image and Summary'
                    else:
                        contentTypeOptionsString = contentTypeOptionsString + option
                    contentTypeOptionsString = contentTypeOptionsString+ '</option>'
                    
                contentTypeOptionsString = contentTypeOptionsString + '</select>'
                compPage['contentType'] = contentTypeOptionsString
                #compPage['contentType'] = currentCompPage.contentType
                
                if currentCompPage.contentType == 'userInput':
                    compPage['summary'] = currentCompPage.summary
                    if currentCompPage.summaryUrl != 'N/A':
                        compPage['summaryUrl'] = currentCompPage.summaryUrl
                    if currentCompPage.graphicUrl != 'N/A':
                        compPage['graphicUrl'] = currentCompPage.graphicUrl
                else:
                    compPage['content'] = currentCompPage.content
                if currentCompPage.thumbnailUrl != 'N/A':
                    compPage['thumbnailUrl'] = currentCompPage.thumbnailUrl
                pagekey = currentCompPage.key()
                compPage['compPageId'] = pagekey.id()
                context = {'title' : 'Edit Composite Page',
                           'user' : userName,
                           'logoutUrl' : logoutUrl,
                           'compPage' : compPage,}
                tmpl = path.join(path.dirname(__file__), 'compositeManager.html')
                html = render(tmpl, context)
                self.response.out.write(html)
""" --- """



""" Main function which handles url mappings"""
application = webapp.WSGIApplication([('/artist/composite-manager', CompositeManagerHandler),
                                      ('/artist/newcomposite', NewCompositeHandler),
                                      ('/artist/redirectcomposite', RedirectCompositeHandler),
                                      ('/artist/editcomposite', EditCompositeHandler),],
                                       debug=True)
def main():
    util.run_wsgi_app(application)
if __name__ == '__main__':
    main()
""" --- """
