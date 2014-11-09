# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com> on Sat Nov  1 15:35:21 2014
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

# Clean the source to just a set of words, one word per row
#
# Re-map the characters to match the font in use, per
# https://www.metafilter.com/144324/50000-repetitions-of-the-word-meow#5810167

import logging
import coloredlogs
coloredlogs.install(level=logging.DEBUG)

import re

marker = re.compile('<[^>]+>')

filename = 'text16e6.evt'

out = open('words.txt', 'w')

charmap = {'a': 'a',
           'o': 'o',
           'y': '9',
           'i': 'i',
           'e': 'c',
           'k': 'h',
           't': 'k',
           'p': 'g',
           'f': 'f',
           'd': '8',
           's': 's',
           'g': '*',
           'l': 'e',
           'r': 'y',
           'm': 'p',
           'n': 'N',
           'q': '4',
           'x': '|',
           }

dualmap = {'ch': '1',
           'sh': '2',
           'ckh': 'H',
           'cth': 'K',
           'cph': 'G',
           'cfh': 'F'
           }
single_pattern = re.compile('|'.join(charmap.keys()))
dual_pattern = re.compile('|'.join(dualmap.keys()))

for line in open(filename):
    line = line.strip()
    if line.startswith('#'):
        continue
    if '%' in line or '{' in line or '!!' in line or '*' in line or '!' in line:
        continue
    line = marker.sub('', line)
    line = line.strip()
    line = line.replace('-', '')
    line = line.replace('=', '')

    # ht http://stackoverflow.com/a/23720594/662625 for 'split with multiple chars'
    for word in filter(None, re.split("[,\.]+", line)):
        # Replace the duals first
        old_word = word

        # ht http://stackoverflow.com/a/2400577/662625 for 'replace with dict'
        word = dual_pattern.sub(lambda x: dualmap[x.group()], word)
        word = single_pattern.sub(lambda x: charmap[x.group()], word)
        
        logging.info("Replaced {} with {}".format(old_word, word))
        out.write(word + "\n")
