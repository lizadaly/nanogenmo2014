# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com>
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

import logging

logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.propagate = False

import requests
import random
from StringIO import StringIO
import xml.etree.ElementTree as ET
import flickrapi
from PIL import Image
import os.path
import colorsys

from secret import FLICKR_KEY
from seraphs import BUILD_DIR

IA_METADATA_URL = 'https://archive.org/metadata/{}'

FLICKR_USER_ID = '126377022@N07'  # The Internet Archive's Flickr ID
MAX_PHOTOS_PER_PAGE = 5
MIN_LIGHTNESS = 200

class BookImage(object):
    def __init__(self, url, width, height, primary_color):
        self.url = url
        self.width = width
        self.height = height
        self.primary_color = primary_color

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
                         extras='url_o',
                         sort='relevance')

    count = 0

    # Randomize the result set
    photos = list(photos)
    random.shuffle(photos)

    for photo in photos:

        logging.debug(ET.tostring(photo))

        img_url = photo.get('url_o')

        # info = flickr.photos_getInfo(photo_id=photo.get('id'), secret=photo.get('secret'))
        # logging.debug(ET.tostring(info))        

        img_file = requests.get(img_url, stream=True)
        img_file.raw.decode_content = True
        im = Image.open(StringIO(img_file.raw.read()))

        # Main colors
        colors = max(im.getcolors(im.size[0] * im.size[1]))[1]  # 2nd value in the tuple is the RGB color set

        try:
            hls = colorsys.rgb_to_hls(colors[0], colors[1], colors[2])
        except TypeError:
            continue

        lightness = int(hls[1])

        # Skip any images without a light primary color (lazy way of finding background)
        if lightness < MIN_LIGHTNESS:
            logging.debug("Skipping dark image")
            continue

        # Convert to greyscale
        # img = img.convert('LA')

        img_filename = "{}.png".format(photo.get('id'))

        img_dir = os.path.join(BUILD_DIR, img_filename)

        im.save(img_dir)

        book_images.append(BookImage(url=img_filename,
                                     width=im.size[0],
                                     height=im.size[1],
                                     primary_color=colors))

        #logging.debug(ET.tostring(info))
        count += 1
        if count > MAX_PHOTOS_PER_PAGE:
            break

    return book_images


if __name__ == '__main__':
    flickr_search()
    
