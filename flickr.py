# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com>
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

import logging

logging.basicConfig(level=logging.INFO)

import requests
import json
from StringIO import StringIO
import struct
import xml.etree.ElementTree as ET
import flickrapi
from PIL import Image

from secret import FLICKR_KEY

IA_METADATA_URL = 'https://archive.org/metadata/{}'

FLICKR_USER_ID = '126377022@N07'  # The Internet Archive's Flickr ID
MAX_PHOTOS_PER_PAGE = 1

class BookImage(object):
    def __init__(self, url, width, height):
        self.url = url
        self.width = width
        self.height = height

def get_ia_data(info):
    '''Get metadata from the IA about the original title'''
    for tag in info.iter('tag'):
        if tag.get('raw').startswith('bookid'):
            bookid = tag.get('raw').replace('bookid:', '')
            
            # Get some data from IA about it
            resp = requests.get(IA_METADATA_URL.format(bookid))
            return resp
    
        
def flickr_search(text, tags='bookcentury1700'):
    '''Request images from the IA Flickr account with the given century tags and the related text'''
    book_images = []

    flickr = flickrapi.FlickrAPI(FLICKR_KEY, format='etree')
    photos = flickr.walk(user_id=FLICKR_USER_ID,
                         per_page=50,
                         text=text,
                         tag_mode='all',
                         tags=tags,
                         sort='relevance')

    count = 0
    
    for photo in photos:

        logging.info(ET.tostring(photo))
        
        img_url = "https://farm{farm_id}.staticflickr.com/{server_id}/{photo_id}_{secret}.jpg".format(farm_id=photo.get('farm'),
                                                                                                      server_id=photo.get('server'),
                                                                                                      photo_id=photo.get('id'),
                                                                                                      secret=photo.get('secret'))
        img_file = requests.get(img_url, stream=True)
        img_file.raw.decode_content = True
        img = Image.open(StringIO(img_file.raw.read()))
        
        info = flickr.photos_getInfo(photo_id=photo.get('id'), secret=photo.get('secret'))

        logging.debug(ET.tostring(info))

        book_images.append(BookImage(url=img_url,
                                     width=img.size[0],
                                     height=img.size[1]))
                          
        #logging.debug(ET.tostring(info))
        count += 1
        if count > MAX_PHOTOS_PER_PAGE:
            break

    return book_images


if __name__ == '__main__':
    flickr_search()
    
