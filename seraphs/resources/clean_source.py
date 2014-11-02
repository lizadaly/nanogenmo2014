# encoding: utf-8
# Created by Liza Daly <lizadaly@gmail.com> on Sat Nov  1 15:35:21 2014
#
# This work is in the public domain http://creativecommons.org/publicdomain/zero/1.0/
# Libraries used by this work may be commercial or have other copyright restrictions.

# Clean the EVA source to just a set of words, one word per row

import re

marker = re.compile('<[^>]+>')

filename = 'text16e6.evt'

out = open('words.txt', 'w')

for line in open(filename):
    line = line.strip()
    if line.startswith('#'):
        continue
    if '%' in line or '{' in line or '!!' in line:
        continue
    line = marker.sub('', line)
    line = line.strip()
    line = line.replace('-', '')
    line = line.replace('=', '')    
    for word in line.split('.'):
        out.write(word + "\n")
