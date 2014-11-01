# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com> on Sat Nov  1 15:35:21 2014
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

import os.path
import flickr
import random
import shutil

from jinja2 import Environment, PackageLoader
from seraphs import BUILD_DIR
env = Environment(loader=PackageLoader('seraphs', 'templates'))

# The sections of the books that will be thematically related, based on the Voynich sections
BOOK_SECTIONS = ('herb', 'astronomy', 'biology', 'astrology', 'medicine', 'alchemy',)
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def fill_template_page(section, images, words):
    template = env.get_template('1.html')
    return template.render(images=images, section=section, color=images[0].primary_color, words=words)

if __name__ == '__main__':

    # Delete previous runs and re-create build dir
    shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)
        
    # Delete
    words = [word.strip() for word in open(os.path.join(THIS_DIR, 'resources/words.txt')).readlines()]
    random.shuffle(words)
    
    for section in BOOK_SECTIONS[0:1]:
        images = flickr.flickr_search(section)
        rendered_template = fill_template_page(section, images, words)
        print rendered_template        
