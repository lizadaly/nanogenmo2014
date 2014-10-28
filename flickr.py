# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com>
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries called by this work may be commercial or have other copyright restrictions

import xml.etree.ElementTree as ET
import flickrapi
from secret import FLICKR_KEY

FLICKR_USER_ID = '126377022@N07'  # The Internet Archive's Flickr ID

def flickr_search():
    flickr = flickrapi.FlickrAPI(FLICKR_KEY, format='etree')
    for photo in flickr.walk(user_id=FLICKR_USER_ID,
                             text='bird',
                             tag_mode='all',
                             tags='bookcentury1500',
                             sort='relevance'):

        ## https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg

        img = "https://farm{farm_id}.staticflickr.com/{server_id}/{photo_id}_{secret}.jpg".format(
            farm_id=photo.get('farm'),
            server_id=photo.get('server'),
            photo_id=photo.get('id'),
            secret=photo.get('secret'))

        print '<img src="{}">'.format(img)

if __name__ == '__main__':
    flickr_search()
    
