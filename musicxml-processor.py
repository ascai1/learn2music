#!/usr/bin/python
# author: ascai
# I whipped this up in order to make the MusicXML files easier to diff.
# This basically collapses all the notes, and other children of the
# "measure" elem, into a single line each. Run this on your file before
# you commit, like './musicxml-processor.py my_comp.xml'. You can also
# provide an optional destination file, or specify '--destination=stdout'
# to print to stdout.

import xml.etree.ElementTree as ET
import argparse
import os
import os.path
import re
from sys import stdout

def get_header(xml_filename):
    with open(xml_filename) as xml_file:
        header = ''
        while True:
            line = xml_file.readline()
            if not line or line.strip() and not re.match('^<[?!]', line):
                return header
            header += line

def reformat_elem(elem, level=0, strip_text_newline=False,
        strip_tail_newline=False):
    if strip_text_newline:
        if elem.text and not elem.text.strip():
            elem.text = None
    elif len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = '\n' + ' ' * (level + 1)

    if strip_tail_newline:
        if elem.tail and not elem.tail.strip():
            elem.tail = None
    elif level:
        if not elem.tail and elem.tail.strip():
            elem.tail = '\n' + ' ' * level

    for sub_elem in elem:
        reformat_elem(sub_elem, level + 1,
                strip_text_newline or (elem.tag == 'measure'),
                strip_text_newline)

    if not strip_text_newline and len(elem):
        last_elem = elem[-1]
        if not last_elem.tail or not last_elem.tail.strip():
            last_elem.tail = '\n' + ' ' * level

def reformat(xml_filename, destination):
    header = get_header(xml_filename)
    tree = ET.parse(xml_filename)
    reformat_elem(tree.getroot())
    if destination == 'stdout':
        stdout.write(header)
        tree.write(stdout)
        return

    remove_orig = False
    if not destination:
        remove_orig = True
        destination = xml_filename + '.tmp'
    with open(destination, 'w') as outfile:
        outfile.write(header)
        tree.write(outfile)
    if remove_orig:
        os.remove(xml_filename)
        os.rename(destination, xml_filename)

parser = argparse.ArgumentParser()
parser.add_argument('xml_filename')
parser.add_argument('--destination')
args = parser.parse_args()
reformat(args.xml_filename, args.destination)
