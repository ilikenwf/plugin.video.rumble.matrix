import sys
try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
import re
import os
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
try:
    import json
except:
    import simplejson as json

BASE_URL = 'https://rumble.com'
PLUGIN_URL = sys.argv[0]
PLUGIN_ID = int(sys.argv[1])
PLUGIN_NAME = PLUGIN_URL.replace("plugin://","")

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')

HOME_DIR = 'special://home/addons/{0}'.format(PLUGIN_NAME)
RESOURCE_DIR = HOME_DIR + 'resources/'
MEDIA_DIR = RESOURCE_DIR + 'media/'

#language
__language__ = ADDON.getLocalizedString

try:
    profile = xbmcvfs.translatePath(ADDON.getAddonInfo('profile').decode('utf-8'))
except:
    profile = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))

lang = ADDON.getSetting('lang')
favorites = os.path.join(profile, 'favorites.dat')

if os.path.exists(favorites)==True:
    FAV = open(favorites).read()
else:
    FAV = []


def notify(message,name=False,iconimage=False,timeShown=5000):
    if name and iconimage:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (name, message, timeShown, iconimage))
    else:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (ADDON_NAME, message, timeShown, ADDON_ICON))


def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text


def get_search_string(heading='', message=''):
    """Ask the user for a search string"""
    search_string = None
    keyboard = xbmc.Keyboard(message, heading)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_string = to_unicode(keyboard.getText())
    return search_string


def getRequest(url, ref=''):

    try:
        if ref == '':
            ref = url

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders=[('Accept-Language', 'en-gb,en;q=0.5'),('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'),('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'), ('Referer', ref)]
        data = opener.open(url).read()
        response = data.decode('utf-8')
    except:
        response = ''

    return response


# main menu
def home_menu():

    # Search
    addDir('[B]'+xbmc.getLocalizedString(137)+'[/B]','',1,MEDIA_DIR + 'search.png','','','')
    # Favorites
    addDir('[B]'+xbmc.getLocalizedString(1036)+'[/B]','',7,MEDIA_DIR + 'favorite.png','','','')
    # News
    addDir('[B]'+xbmc.getLocalizedString(29916)+'[/B]',BASE_URL+'/category/news',3,MEDIA_DIR + 'news.png','','','other')
    # Viral
    addDir('[B]'+__language__(30050)+'[/B]',BASE_URL+'/category/viral',3,MEDIA_DIR + 'viral.png','','','other')
    # Podcasts
    addDir('[B]'+__language__(30051)+'[/B]',BASE_URL+'/category/podcasts',3,MEDIA_DIR +'podcast.png','','','other')
    # Battle Leaderboard
    addDir('[B]'+__language__(30052)+'[/B]',BASE_URL+'/battle-leaderboard',3,MEDIA_DIR + 'leader.png','','','top')
    # Entertainment
    addDir('[B]'+__language__(30053)+'[/B]',BASE_URL+'/category/entertainment',3,MEDIA_DIR + 'entertaiment.png','','','other')
    # Sports
    addDir('[B]'+xbmc.getLocalizedString(19548)+'[/B]',BASE_URL+'/category/sports',3,MEDIA_DIR + 'sports.png','','','other')
    # Science
    addDir('[B]'+xbmc.getLocalizedString(29948)+'[/B]',BASE_URL+'/category/science',3,MEDIA_DIR + 'science.png','','','other')
    # Technology
    addDir('[B]'+__language__(30054)+'[/B]',BASE_URL+'/category/technology',3,MEDIA_DIR + 'technology.png','','','other')
    # Vlogs
    addDir('[B]'+__language__(30055)+'[/B]',BASE_URL+'/category/vlogs',3,MEDIA_DIR + 'vlog.png','','','other')
    # Settings
    addDir('[B]'+xbmc.getLocalizedString(5)+'[/B]','',8,MEDIA_DIR + 'settings.png','','','')
    SetView('WideList')
    xbmcplugin.endOfDirectory(PLUGIN_ID, cacheToDisc=False)


# search menu
def search_menu():

    # Search Video
    addDir('[B]'+__language__(30100)+'[/B]',BASE_URL+'/search/video?q=',2,MEDIA_DIR + 'search.png','','','video')
    # Search Channel
    addDir('[B]'+__language__(30101)+'[/B]',BASE_URL+'/search/channel?q=',2,MEDIA_DIR + 'search.png','','','channel')
    SetView('WideList')
    xbmcplugin.endOfDirectory(PLUGIN_ID)


def pagination(url,page,cat,search=False):

    if url > '':

        if search and cat == 'video':
            pageUrl = url + search + "&page=" + str(int(page))
        elif cat == 'channel' or cat == 'other':
            pageUrl = url + "?page=" + str(int(page))

        if int(page) == 1:
            if search:
                status, total = list_rumble(url+search,cat)
            else:
                status, total = list_rumble(url,cat)
        else:
            status, total = list_rumble(pageUrl,cat)

        if search and status and cat == 'video' and int(page) < 10 and int(total) > 15:
            name = "[B]"+__language__(30150) + " " + str(int(page) + 1) + "[/B]"
            li=xbmcgui.ListItem(name)
            u=sys.argv[0] + "?mode=3&name=" + urllib.quote_plus(name) + \
            "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1) + "&cat=" + urllib.quote_plus(cat)+ "&search=" + urllib.quote_plus(search)
            xbmcplugin.addDirectoryItem(PLUGIN_ID, u, li, True)
        elif not search and cat == 'channel' and status and int(page) < 10 and int(total) > 15:
            name = "[B]"+__language__(30150) + " " + str(int(page) + 1) + "[/B]"
            li=xbmcgui.ListItem(name)
            u=sys.argv[0] + "?mode=3&name=" + urllib.quote_plus(name) + \
            "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1) + "&cat=" + urllib.quote_plus(cat)
            xbmcplugin.addDirectoryItem(PLUGIN_ID, u, li, True)
        elif not search and cat == 'other' and status and int(page) < 10 and int(total) > 15:
            name = "[B]"+__language__(30150) + " " + str(int(page) + 1) + "[/B]"
            li=xbmcgui.ListItem(name)
            u=sys.argv[0] + "?mode=3&name=" + urllib.quote_plus(name) + \
            "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1) + "&cat=" + urllib.quote_plus(cat)
            xbmcplugin.addDirectoryItem(PLUGIN_ID, u, li, True)
    SetView('WideList')
    xbmcplugin.endOfDirectory(PLUGIN_ID)


def get_image(data,id):
    image_re = re.compile("i.user-image--img--id-"+str(id)+".+?{ background-image: url(.+?);", re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
    if image_re !=[]:
        image = str(image_re[0]).replace('(', '').replace(')', '')
    else:
        image = ''
    return image


def list_rumble(url,cat):

    total = 0
    status = False

    if 'search' in url and cat == 'video':
        data = getRequest(url, '')
        videos_re = re.compile('<h3 class=video-item--title>(.+?)</h3><a class=video-item--a href=(.+?)><img class=video-item--img src=(.+?) alt.+?<div class=ellipsis-1>(.+?)<.+?</div>.+?datetime=(.+?)-(.+?)-(.+?)T', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
        if videos_re !=[]:
            for name, link, img, channel, year, month, day in videos_re:
                if int(lang) == 0:
                    time_ = month+'/'+day+'/'+year
                else:
                    time_ = day+'/'+month+'/'+year
                name2 = '[B]'+name+'[/B]\n[COLOR gold]'+channel+' - [COLOR lime]'+time_+'[/COLOR]'
                #open get url and open player
                addDir(name2.encode('utf-8', 'ignore'),(BASE_URL+link).encode('utf-8'),4,str(img),str(img),'',cat.encode('utf-8'),False,True,1)
            total = len(videos_re)
            status = True

    elif 'search' in url and cat == 'channel':
        data = getRequest(url, '')
        channel_re = re.compile("<li.+?video-listing-entry.+?<a class=channel-item--a href=(.+?)>.+?<i class='user-image user-image--img user-image--img--id-(.+?)'>.+?<h3 class=channel-item--title>(.+?)</h3>.+?<span class=channel-item--subscribers>(.+?) subscribers</span>.+?</li>",re.DOTALL).findall(data)
        if channel_re !=[]:
            for link, img_id, channel_name, subscribers in channel_re:
                img = get_image(data,img_id)
                name2 = '[B]'+channel_name+'[/B]\n[COLOR palegreen]'+subscribers+' [COLOR yellow]'+__language__(30155)+'[/COLOR]'
                #open get url and open player
                addDir(name2.encode('utf-8', 'ignore'),(BASE_URL+link).encode('utf-8'),3,str(img),str(img),'',cat.encode('utf-8'),True,True)
            total = len(channel_re)
            status = True

    elif cat == 'channel' or cat == 'other':
        data = getRequest(url, '')
        videos_from_channel_re = re.compile('<h3 class=video-item--title>(.+?)</h3><a class=video-item--a href=(.+?)><img class=video-item--img src=(.+?) alt.+?<div class=ellipsis-1>(.+?)<.+?</div>.+?datetime=(.+?)-(.+?)-(.+?)T', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
        if videos_from_channel_re !=[]:
            for name, link, img, channel, year, month, day in videos_from_channel_re:
                if int(lang) == 0:
                    time_ = month+'/'+day+'/'+year
                else:
                    time_ = day+'/'+month+'/'+year
                name2 = '[B]'+name+'[/B]\n[COLOR gold]'+channel+' - [COLOR lime]'+time_+'[/COLOR]'
                #open get url and open player
                addDir(name2.encode('utf-8', 'ignore'),(BASE_URL+link).encode('utf-8'),4,str(img),str(img),'',cat.encode('utf-8'),False,True,2)
            total = len(videos_from_channel_re)
            status = True

    elif cat == 'top':
        data = getRequest(url, '')
        top_battle_re = re.compile('<h3 class=video-item--title>(.+?)</h3><a class=video-item--a href=(.+?)>.+?<img class=video-item--img-img src=(.+?) alt.+?<div class=ellipsis-1>(.+?)<.+?</div>.+?datetime=(.+?)-(.+?)-(.+?)T', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
        if top_battle_re !=[]:
            for name, link, img, channel, year, month, day in top_battle_re:
                if int(lang) == 0:
                    time_ = month+'/'+day+'/'+year
                else:
                    time_ = day+'/'+month+'/'+year
                name2 = '[B]'+name+'[/B]\n[COLOR gold]'+channel+' - [COLOR lime]'+time_+'[/COLOR]'
                #open get url and open player
                addDir(name2.encode('utf-8', 'ignore'),(BASE_URL+link).encode('utf-8'),4,str(img),str(img),'',cat.encode('utf-8'),False,True,2)
            total = len(top_battle_re)
            status = True

    return status, total


def resolver(url):

    # playback options - 0: large to small, 1: small to large, 2: quality select
    playbackMethod = ADDON.getSetting('playbackMethod')

    mediaURL = False

    if playbackMethod == '2':
       urls = []

    data = getRequest(url)
    embed_re = re.compile(',"embedUrl":"(.*?)",', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
    if embed_re:
        data = getRequest(embed_re[0])
        sizes = [ '1080', '720', '480', '360' ]

        # reverses array - small to large
        if playbackMethod == '1':
            sizes = sizes[::-1]

        for quality in sizes:

            matches = re.compile('"' + quality + '":.+?url.+?:"(.*?)",', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)

            if matches:
                if playbackMethod == '2':
                    urls.append(( quality, matches[0] ))
                else:
                    mediaURL = matches[0]
                    break

        # quality select
        if playbackMethod == '2':
            if len(urls) > 0:
                selectedIndex = xbmcgui.Dialog().select(
                    'Select Quality', [(sourceItem[0] or '?') for sourceItem in urls]
                )
                if selectedIndex != -1:
                    mediaURL = urls[selectedIndex][1]

    if mediaURL:
        mediaURL = mediaURL.replace('\/', '/')

    return mediaURL


def play_video(name, url, iconimage, play=2):

    url = resolver(url)

    if url:

        li = xbmcgui.ListItem(name, path=url)
        li.setArt({"icon": iconimage, "thumb": iconimage})
        li.setInfo(type='video', infoLabels={'Title': name, 'plot': ''})

        if play == 1:
            xbmc.Player().play(item=url, listitem=li)
        elif play == 2:
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

    else:
        xbmcgui.Dialog().ok( 'Error', 'Video not found' )


def search_items(url,cat):
    vq = get_search_string(heading="Search")
    if ( not vq ): return False, 0
    title = urllib.quote_plus(vq)
    pagination(url,1,cat,title)


def getFavorites():
    try:
        try:
            items = json.loads(open(favorites).read())
        except:
            items = ''
        total = len(items)
        if int(total) > 0:
            for i in items:
                name = i[0]
                url = i[1]
                mode = i[2]
                iconimage = i[3]
                fanArt = i[4]
                description = i[5]
                cat = i[6]
                folder = i[7]
                if folder == 'True':
                    folder = True
                else:
                    folder = False
                play = i[8]


                addDir(name.encode('utf-8', 'ignore'),url.encode('utf-8'),mode,str(iconimage),str(fanArt),str(description).encode('utf-8', 'ignore'),cat.encode('utf-8'),folder,True,int(play))
            SetView('WideList')
            xbmcplugin.endOfDirectory(PLUGIN_ID)
        else:
            xbmcgui.Dialog().ok('[B]'+xbmc.getLocalizedString(14117)+'[/B]',__language__(30155))
    except:
        SetView('WideList')
        xbmcplugin.endOfDirectory(PLUGIN_ID)


def addFavorite(name,url,fav_mode,iconimage,fanart,description,cat,folder,play):
    favList = []
    if os.path.exists(favorites)==False:
        addonID = xbmcaddon.Addon().getAddonInfo('id')
        addon_data_path = xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data', addonID))
        if os.path.exists(addon_data_path)==False:
            os.mkdir(addon_data_path)
        xbmc.sleep(7)
        favList.append((name,url,fav_mode,iconimage,fanart,description,cat,folder,play))
        a = open(favorites, "w")
        a.write(json.dumps(favList))
        a.close()
        notify(__language__(30152),name,iconimage)
        #xbmc.executebuiltin("XBMC.Container.Refresh")
    else:
        a = open(favorites).read()
        data = json.loads(a)
        data.append((name,url,fav_mode,iconimage,fanart,description,cat,folder,play))
        b = open(favorites, "w")
        b.write(json.dumps(data))
        b.close()
        notify(__language__(30152),name,iconimage)
        #xbmc.executebuiltin("XBMC.Container.Refresh")


def rmFavorite(name):
    data = json.loads(open(favorites).read())
    for index in range(len(data)):
        if data[index][0]==name:
            del data[index]
            b = open(favorites, "w")
            b.write(json.dumps(data))
            b.close()
            break
    notify(__language__(30154))
    #xbmc.executebuiltin("XBMC.Container.Refresh")


def addDir(name,url,mode,iconimage,fanart,description,cat,folder=True,favorite=False,play=False):
    if play:
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)+"&cat="+urllib.quote_plus(cat)+"&play="+str(play)
    else:
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)+"&cat="+urllib.quote_plus(cat)
    li=xbmcgui.ListItem(name)
    if folder:
        li.setArt({'icon': 'DefaultFolder.png', 'thumb': iconimage})
    else:
        li.setArt({'icon': 'DefaultVideo.png', 'thumb': iconimage})
    if play == 2 and mode == 4:
        li.setProperty('IsPlayable', 'true')
    li.setInfo(type='Video', infoLabels={'Title': name, 'Plot': description})
    if fanart > '':
        li.setProperty('fanart_image', fanart)
    else:
        li.setProperty('fanart_image', HOME_DIR+'fanart.jpg')
    if favorite:
        try:
            name_fav = json.dumps(name.decode('utf-8'))
        except:
            name_fav = name.decode('utf-8')
        try:
            contextMenu = []
            if name_fav in FAV:
                contextMenu.append((__language__(30153),'RunPlugin(%s?mode=6&name=%s)'%(sys.argv[0], urllib.quote_plus(name))))
            else:
                fav_params = ('%s?mode=5&name=%s&url=%s&iconimage=%s&fanart=%s&description=%s&cat=%s&folder=%s&play=%s&fav_mode=%s'%(sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), urllib.quote_plus(fanart), urllib.quote_plus(description), urllib.quote_plus(cat), urllib.quote_plus(str(folder)), urllib.quote_plus(str(play)), str(mode)))
                contextMenu.append((__language__(30151),'RunPlugin(%s)' %fav_params))
            li.addContextMenuItems(contextMenu)
        except:
            pass
    xbmcplugin.addDirectoryItem(handle=PLUGIN_ID, url=u, listitem=li, isFolder=folder)


def SetView(name):

    if name == 'Fanart':
        view_num = 502
    elif name == 'Wall':
        view_num = 500
    elif name == 'WideList':
        view_num = 55
    elif name == 'InfoWall':
        view_num = 54
    elif name == 'Shift':
        view_num = 53
    elif name == 'Poster':
        view_num = 51
    elif name == 'List':
        view_num = 50
    else:
        view_num = 0

    if view_num > 0:
        try:
            xbmc.executebuiltin('Container.SetViewMode(' + str( view_num ) + ')')
        except:
            pass


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param


def main():
    params=get_params()
    url=None
    name=None
    mode=None
    iconimage=None
    fanart=None
    description=None
    cat=None
    search=None
    folder=None
    fav_mode=None
    play=1
    page=1

    try:
        url=urllib.unquote_plus(params["url"])
    except:
        pass
    try:
        name=urllib.unquote_plus(params["name"])
    except:
        pass
    try:
        iconimage=urllib.unquote_plus(params["iconimage"])
    except:
        pass
    try:
        mode=int(params["mode"])
    except:
        pass
    try:
        fanart=urllib.unquote_plus(params["fanart"])
    except:
        pass
    try:
        description=urllib.unquote_plus(params["description"])
    except:
        pass

    try:
        subtitle=urllib.unquote_plus(params["subtitle"])
    except:
        pass
    try:
        cat=urllib.unquote_plus(params["cat"])
    except:
        pass
    try:
        search=urllib.unquote_plus(params["search"])
    except:
        pass
    try:
        page=int(params["page"])
    except:
        pass
    try:
        folder=urllib.unquote_plus(params["folder"])
    except:
        pass
    try:
        fav_mode=int(params["fav_mode"])
    except:
        pass
    try:
        play=int(params["play"])
    except:
        pass

    if mode==None:
        home_menu()
    elif mode==1:
        search_menu()
    elif mode==2:
        search_items(url,cat)
    elif mode==3:
        if search and search !=None:
            pagination(url,page,cat,search)
        else:
            pagination(url,page,cat)
    elif mode==4:
        play_video(name, url, iconimage, play)
    elif mode==5:
        try:
            name = name.split('\\ ')[1]
        except:
            pass
        try:
            name = name.split('  - ')[0]
        except:
            pass
        addFavorite(name,url,fav_mode,iconimage,fanart,description,cat,str(folder),str(play))
    elif mode==6:
        try:
            name = name.split('\\ ')[1]
        except:
            pass
        try:
            name = name.split('  - ')[0]
        except:
            pass
        rmFavorite(name)
    elif mode==7:
        getFavorites()
    elif mode==8:
        xbmcaddon.Addon().openSettings()


if __name__ == "__main__":
	main()
