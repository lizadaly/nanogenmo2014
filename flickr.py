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


from secret import FLICKR_KEY

IA_METADATA_URL = 'https://archive.org/metadata/{}'

FLICKR_USER_ID = '126377022@N07'  # The Internet Archive's Flickr ID
MAX_PHOTOS_PER_PAGE = 5

class Image(object):
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
                         per_page=5,
                         text=text,
                         tag_mode='all',
                         tags=tags,
                         sort='relevance')

    count = 0
    
    for photo in photos:

        logging.info(ET.tostring(photo))
        
        img = "https://farm{farm_id}.staticflickr.com/{server_id}/{photo_id}_{secret}.jpg".format(
            farm_id=photo.get('farm'),
            server_id=photo.get('server'),
            photo_id=photo.get('id'),
            secret=photo.get('secret'))
        img_file = requests.get(img, stream=True)
        img_file.raw.decode_content = True
        img_data = img_file.raw.read()
        content_type, width, height = get_image_info(img_data)
        
        info = flickr.photos_getInfo(photo_id=photo.get('id'), secret=photo.get('secret'))

        logging.debug(ET.tostring(info))

        book_images.append(Image(url=img,
                                 width=width,
                                 height=height))
                          
        #logging.debug(ET.tostring(info))
        count += 1
        if count > MAX_PHOTOS_PER_PAGE:
            break

    return book_images

# http://markasread.net/post/17551554979/get-image-size-info-using-pure-python-code
def get_image_info(data):
    """
    Return (content_type, width, height) for a given img file content
    no requirements
    """
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    if (size >= 2) and data.startswith('\377\330'):
        content_type = 'image/jpeg'
        jpeg = StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = jpeg.read
                while (ord(b) == 0xFF): b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


if __name__ == '__main__':
    flickr_search()
    
