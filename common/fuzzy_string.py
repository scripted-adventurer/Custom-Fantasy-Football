# -*- coding: utf-8 -*-

'''A module to handle matching people's names on the basis of the phonetic 
representation of each word in the name. Encoding creates an NYSIIS phonetic 
encoding for the whole name (as a single string) by concatenating the encoding 
of each word in the name (splitting hyphenated names).'''

import re
import fuzzy

def encode_name(name):
  names = re.split(r'\s|-', name)
  phonetics = []
  for name in names:
    phonetics.append(fuzzy.nysiis(name))
  return ''.join(phonetics)