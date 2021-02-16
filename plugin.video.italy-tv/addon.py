import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import re
import requests
import urllib
import urlparse
from bs4 import BeautifulSoup

# https://forum.kodi.tv/showthread.php?tid=324570

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Referer': 'https://easysite.one/'
}

addon = xbmcaddon.Addon()

_pid = sys.argv[0]
_handle = int(sys.argv[1])


def list_channels():
  xbmcplugin.setPluginCategory(_handle, 'Italy TV')
  xbmcplugin.setContent(_handle, 'videos')

  html_doc = requests.get("https://www.livehere.one/", headers=headers).content
  #xbmc.log(html_doc, xbmc.LOGNOTICE)
  soup = BeautifulSoup(html_doc, 'html.parser')

  channels_cols = soup.find('ul', 'columns').find_all('ul', 'list')

  for channels_col in channels_cols:
    header = channels_col.find('li', 'header')
    header_title = "[COLOR red][B][UPPERCASE]{}[/UPPERCASE][/B][/COLOR]".format(header.getText().strip())

    headerItem = xbmcgui.ListItem(header_title)
    headerItem.setInfo('video', {'title': header_title, 'mediatype': 'video'})
    headerItem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle=_handle, url="", listitem=headerItem, isFolder=False)

    xbmc.log("---------------------------", xbmc.LOGNOTICE)
    xbmc.log(header_title, xbmc.LOGNOTICE)

    channels_list = channels_col.find_all('li', ['menu-item', 'menu-item-type-custom', 'menu-item-object-custom', 'level2'])
    for channel in channels_list:
      link = channel.find('a')
      link_title = link.getText().strip()

      videoItem = xbmcgui.ListItem(link_title)
      videoItem.setInfo('video', {'title': link_title, 'mediatype': 'video'})
      data = {
          "action": "scrape",
          "title": link_title,
          "link" : link.get('href')
          }
      xbmcplugin.addDirectoryItem(handle=_handle, url='{0}?{1}'.format(_pid, urllib.urlencode(data)), listitem=videoItem, isFolder=True)
      xbmc.log("{}: {}".format(link_title, link.get('href')), xbmc.LOGNOTICE)

    xbmc.log("^^^^^^^^^^^^^^^^^^^^^^^^^^^", xbmc.LOGNOTICE)

  xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
  xbmcplugin.endOfDirectory(_handle)


def list_links(params):
  xbmcplugin.setPluginCategory(_handle, 'Italy TV')
  xbmcplugin.setContent(_handle, 'videos')

  html_out = requests.get(params['link'][0], headers=headers).content
  #xbmc.log(html_out, xbmc.LOGNOTICE)
  soup_out = BeautifulSoup(html_out, 'html.parser')

  iframes_out = soup_out.find_all('iframe')
  for iframe_out in iframes_out:
    html_in = requests.get(iframe_out.get('src'), headers=headers).content
    #xbmc.log(html_in, xbmc.LOGNOTICE)
    soup_in = BeautifulSoup(html_in, 'html.parser')

    c = 1

    iframes_in = soup_in.find_all('iframe')
    for link in iframes_in:
      link_title = "Link {}".format(c)
      c += 1
      link_strip = link.get('src').strip()

      videoItem = xbmcgui.ListItem(link_title)
      videoItem.setInfo('video', {'title': link_title, 'mediatype': 'video'})
      videoItem.setProperty('IsPlayable', 'true')
      data = {
          "action": "play",
          "url" : link_strip,
          "quality": "best",
          "title": link_title,
          "image": ""
          }
      xbmcplugin.addDirectoryItem(handle=_handle, url='plugin://plugin.video.streamlink-tester/?{1}'.format(_pid, urllib.urlencode(data)), listitem=videoItem, isFolder=False)
      #xbmc.log(link_title, xbmc.LOGNOTICE)

    links_list = re.findall("http.*?m3u8", html_in)

    for link in links_list:
      link_title = "Link {}".format(c)
      c += 1
      link_strip = link.strip()

      videoItem = xbmcgui.ListItem(link_title)
      videoItem.setInfo('video', {'title': link_title, 'mediatype': 'video'})
      videoItem.setProperty('IsPlayable', 'true')
      data = {
          "action": "play",
          "title": link_title,
          "link" : link_strip
          }
      xbmcplugin.addDirectoryItem(handle=_handle, url='{0}?{1}'.format(_pid, urllib.urlencode(data)), listitem=videoItem, isFolder=False)
      #xbmc.log(link_title, xbmc.LOGNOTICE)

  xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
  xbmcplugin.endOfDirectory(_handle)


def play_video(params):
  xbmcplugin.setResolvedUrl(_handle, True, listitem=xbmcgui.ListItem(path=params['link'][0]))


xbmc.log(" ".join(sys.argv), xbmc.LOGNOTICE)


def router(paramstring):
  try:
    xbmc.log("paramstring: {}".format(paramstring), xbmc.LOGNOTICE)
    params = urlparse.parse_qs(paramstring)
  except Exception as e:
    xbmc.log("type error: " + str(e), xbmc.LOGERROR)
    params = False

  xbmc.log("params: {}".format(params), xbmc.LOGNOTICE)

  if params:
    if params['action'][0] == 'play':
      play_video(params)
    elif params['action'][0] == 'scrape':
      list_links(params)
    else:
      list_channels()

  else:
    list_channels()

if __name__ == '__main__':
  router(sys.argv[2][1:])
