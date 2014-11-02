# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com> on Sat Nov  1 15:35:21 2014
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

import logging
import coloredlogs
coloredlogs.install(level=logging.DEBUG)

import os
import flickr
import random
import shutil
import pickle
import subprocess
from glob import glob

from jinja2 import Environment, PackageLoader
from seraphs import BUILD_DIR, THIS_DIR, CACHE_DIR

env = Environment(loader=PackageLoader('seraphs', 'templates'))

# The sections of the books that will be thematically related, based on the Voynich sections
BOOK_SECTIONS = ('botany', 'astronomy', 'biology', 'planets', 'anatomy', 'alchemy',)

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def fill_template_page(section_num, section, images, words):

    # Create the title page for the folio
    cover = env.get_template("folio.html")
    cover_image = images.pop()
    cover_rendered = cover.render(image=cover_image, color=cover_image.primary_color, word=words.pop(), section=section)
    out = open(os.path.join(BUILD_DIR, "{}-000.html".format(section)), 'w')
    out.write(cover_rendered)
    
    for i, image in enumerate(images):
        random.shuffle(words)

        if (image.width / 2) > image.height:  # wide landscape
            template_file = 'landscape1.html'
        elif image.width > image.height:  # narrow landscape
            template_file = 'landscape2.html'
        elif image.width < image.height:
            template_file = random.choice(['portrait1.html', 'portrait2.html', 'portrait3.html', 'portrait4.html'])

        template = env.get_template(template_file)
        rendered = template.render(image=image, color=image.primary_color, words=words, section=section)
        out = open(os.path.join(BUILD_DIR, "{}-{:0>3d}.html".format(section, i+1)), 'w')
        out.write(rendered)

if __name__ == '__main__':

    words = [word.strip() for word in open(os.path.join(THIS_DIR, 'resources/words.txt')).readlines()]

    # Delete previous generated output file
    html_files = glob(os.path.join(BUILD_DIR, '*.html'))
    for f in html_files:
        os.unlink(f)

    for i, section in enumerate(BOOK_SECTIONS[0:1]):
        section_cache = os.path.join(CACHE_DIR, section + '.p')

        if os.path.exists(section_cache):
            logging.debug("Loading section {} from cache".format(section))
            images = pickle.load(open(section_cache, 'rb'))
        else:
            logging.debug("{} didn't exist".format(section_cache))

            images = flickr.flickr_search(section)
            pickle.dump(images, open(section_cache, 'wb'))

        random.shuffle(images)
        rendered_template = fill_template_page(i, section, images, words)

    shutil.copy(os.path.join(THIS_DIR, "templates", "styles.css"), BUILD_DIR)
    shutil.copy(os.path.join(THIS_DIR, "resources", "EVA Hand 1.ttf"), BUILD_DIR)
    html_files = glob(os.path.join(BUILD_DIR, '*.html'))
    subprocess.call(["prince",
                     #"--verbose",
                     "-s", os.path.join(BUILD_DIR, "styles.css")] + html_files + [os.path.join(BUILD_DIR, "book.pdf")])
