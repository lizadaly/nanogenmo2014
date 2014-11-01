# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com> on Sat Nov  1 15:35:21 2014
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

import logging

logging.basicConfig(level=logging.DEBUG)

import os
import flickr
import random
import shutil
import pickle
import subprocess

from jinja2 import Environment, PackageLoader
from seraphs import BUILD_DIR, THIS_DIR, CACHE_DIR

env = Environment(loader=PackageLoader('seraphs', 'templates'))

# The sections of the books that will be thematically related, based on the Voynich sections
BOOK_SECTIONS = ('herb', 'astronomy', 'biology', 'astrology', 'medicine', 'alchemy',)

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

IMAGE_CACHE = os.path.join(CACHE_DIR, 'images.p')

def fill_template_page(section, images, words):
    if images[0].width > images[0].height:  # landscape
        template_file = 'landscape1.html'

    template_file = 'landscape1.html'   
    template = env.get_template(template_file)
    return template.render(images=images, section=section, color=images[0].primary_color, words=words)

if __name__ == '__main__':


    # Delete
    words = [word.strip() for word in open(os.path.join(THIS_DIR, 'resources/words.txt')).readlines()]
    random.shuffle(words)

    for section in BOOK_SECTIONS[0:1]:

        if os.path.exists(IMAGE_CACHE):
            logging.debug("Loading from cache")
            images = pickle.load(open(IMAGE_CACHE, 'rb'))
        else:
            logging.debug("{} didn't exist".format(IMAGE_CACHE))
            # Delete previous runs and re-create build dir
            if os.path.exists(BUILD_DIR):
                shutil.rmtree(BUILD_DIR)
            os.makedirs(BUILD_DIR)

            images = flickr.flickr_search(section)
            pickle.dump(images, open(IMAGE_CACHE, 'wb'))

        random.shuffle(images)
        rendered_template = fill_template_page(section, images, words)
        out = open(os.path.join(BUILD_DIR, 'book.html'), 'w')
        out.write(rendered_template)
        
    shutil.copy(os.path.join(THIS_DIR, "templates", "styles.css"), BUILD_DIR)
    shutil.copy(os.path.join(THIS_DIR, "resources", "EVA Hand 1.ttf"), BUILD_DIR)
    subprocess.call(["prince", "--verbose",  "-s", os.path.join(BUILD_DIR, "styles.css"),  os.path.join(BUILD_DIR, 'book.html'), os.path.join(BUILD_DIR, "book.pdf")])
    
                    
