# -*- coding: utf-8 -*-
import sys
import xbmc
import six

from six.moves import urllib

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib

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


def getRequest(url, ref=''):

    try:
        if ref == '':
            ref = url

        cj = cookielib.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders=[('Accept-Language', 'en-gb,en;q=0.5'),('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'),('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'), ('Referer', ref)]
        data = opener.open(url).read()
        response = data.decode('utf-8')
    except:
        response = ''

    return response


def get_params():
    return dict(urllib.parse.parse_qsl(sys.argv[2][1:], keep_blank_values=True))
