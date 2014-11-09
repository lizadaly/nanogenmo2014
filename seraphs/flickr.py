# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com>
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

import logging

logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.propagate = False

from PIL import Image
from StringIO import StringIO

import colorsys
import flickrapi
import os.path
import random
import requests

from secret import FLICKR_KEY
from seraphs import BUILD_DIR

IA_METADATA_URL = 'https://archive.org/metadata/{}'

FLICKR_USER_ID = '126377022@N07'  # The Internet Archive's Flickr ID
MAX_PHOTOS_PER_SECTION = 45
MIN_LIGHTNESS = 200  # Minimize lightness value of the image's primary (background color)
MIN_SIZE = 300  # Minimum length or width of the image, in pixels

class BookImage(object):
    def __init__(self, url, width, height, primary_color, src):
        self.url = url
        self.width = width
        self.height = height
        self.primary_color = primary_color
        self.src = src

def flickr_search(text, tags='bookcentury1700,bookcentury1600'):
    '''Request images from the IA Flickr account with the given century tags and the related text'''
    book_images = []

    flickr = flickrapi.FlickrAPI(FLICKR_KEY, format='etree')
    photos = flickr.walk(user_id=FLICKR_USER_ID,
                         per_page=200,
                         text=text,
                         tag_mode='any',
                         tags=tags,
                         extras='url_o',
                         sort='interestingness-desc')

    count = 0

    # Randomize the result set
    photos = list(photos)
    random.shuffle(photos)

    for photo in photos:

        # Ensure that images are the correct minimize size
        if int(photo.get('height_o')) < MIN_SIZE or int(photo.get('width_o') < MIN_SIZE):
            continue

        img_url = photo.get('url_o')
        img_file = requests.get(img_url, stream=True)
        img_file.raw.decode_content = True
        im = Image.open(StringIO(img_file.raw.read()))

        # Main colors
        colors = max(im.getcolors(im.size[0] * im.size[1]))[1]  # 2nd value in the tuple is the RGB color set

        try:
            hls = colorsys.rgb_to_hls(colors[0], colors[1], colors[2])
        except TypeError as te:
            logging.warn(te)
            continue
        except ZeroDivisionError:
            logging.error("{} {} {}".format(colors[0], colors[1], colors[2]))
            continue

        lightness = int(hls[1])

        # Skip any images without a light primary color (lazy way of finding background), or those that are too small
        if lightness < MIN_LIGHTNESS:
            continue

        img_filename = "{}.png".format(photo.get('id'))
        img_dir = os.path.join(BUILD_DIR, img_filename)

        if not os.path.exists(BUILD_DIR):
            os.makedirs(BUILD_DIR)

        im.save(img_dir)

        src = 'https://www.flickr.com/photos/{}/{}'.format(photo.get('owner'), photo.get('id'))
        book_images.append(BookImage(url=img_filename,
                                     width=im.size[0],
                                     height=im.size[1],
                                     primary_color=colors,
                                     src=src))

        count += 1
        if count > MAX_PHOTOS_PER_SECTION:
            break

    if count < MAX_PHOTOS_PER_SECTION:
        logging.warn("Did not get enough images for section {}: only {}".format(text, count))

    return book_images
