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
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
}

addon = xbmcaddon.Addon()

_pid = sys.argv[0]
_handle = int(sys.argv[1])


def list_channels():
  xbmcplugin.setPluginCategory(_handle, 'UK TV')
  xbmcplugin.setContent(_handle, 'videos')

  channels_list = [
      {"title": "BBC One", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-one-live-stream-bbc-one-live-streaming-bbc-one-online/"},
      {"title": "BBC Two", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-two-live-stream-bbc-two-live-streaming/"},
      {"title": "BBC Four", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-four-live-stream-bbc-four-live-streaming/"},
      {"title": "Cbeebies", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/cbeebies-live-stream-cbeebies-live-streaming/"},
      {"title": "BBC News", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-news-live-stream-bbc-news-live-streaming/"},
      {"title": "ITV One", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-one-live-stream-itv-one-live-streaming/"},
      {"title": "ITV Two", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-two-live-stream-itv-two-live-streaming/"},
      {"title": "ITV Three", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-three-live-stream-itv-three-live-streaming/"},
      {"title": "ITV Four", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-four-live-stream-itv-four-live-streaming/"},
      {"title": "Channel 4", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-four-live-streams/channel-four-live-stream/"},
      {"title": "Channel E4", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-four-live-streams/e4-live-stream/"},
      {"title": "Channel M4", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-four-live-streams/more-4-live-stream/"},
      {"title": "Channel 5", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-five-live-streams/channel-five-live-stream/"},
      {"title": "Channel 5 USA", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-five-live-streams/channel-five-usa-live-stream/"}
      ]

  for channel in channels_list:
    videoItem = xbmcgui.ListItem(label=channel['title'])
    videoItem.setInfo('video', {'title': channel['title'], 'mediatype': 'video'})
    data = {
        "action": "scrape",
        "title": channel['title'],
        "link" : channel['link']
        }
    xbmcplugin.addDirectoryItem(handle=_handle, url='{0}?{1}'.format(_pid, urllib.urlencode(data)), listitem=videoItem, isFolder=True)
    xbmc.log("{}: {}".format(channel['title'], channel['link']), xbmc.LOGNOTICE)

  xbmcplugin.endOfDirectory(_handle)


def list_links(params):
  xbmcplugin.setPluginCategory(_handle, 'UK TV')
  xbmcplugin.setContent(_handle, 'videos')

  html = requests.get(params['link'][0], headers=headers).content
  #xbmc.log(html, xbmc.LOGNOTICE)
  soup = BeautifulSoup(html, 'html.parser')

  c = 1

  iframes = soup.find_all('iframe')
  for link in iframes:
    link_title = "Link {}".format(c)
    c += 1
    link_strip = link.get('src').strip()

    videoItem = xbmcgui.ListItem(label=link_title)
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
