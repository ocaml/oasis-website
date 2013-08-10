#!/usr/bin/python

# Add a panel explaining that the version viewed is not the stable one.

from optparse import OptionParser
from bs4 import BeautifulSoup

import logging
import codecs
import re
import os

DIV_ID = "marknonlatest"

DIV_STYLE = """
background-color: #e9ffe9;
border: 1px solid #609060;
margin: 2em;
padding: 0;
"""
HEADER_STYLE = """
background-color: #70A070;
margin: 0;
color: white;
font-weight: bold;
font-size: 18px;
padding: 4px 0px 4px 9px;
text-shadow: 0 1px rgba(0, 0, 0, 0.5);
"""
NOTE_STYLE = """
margin: 0;
padding: 4px 0px 4px 9px;
font-size: large;
"""

SELECTORS = [ "div.navbar", "div#header" ]


def UnMarkOne(fn):
  soup = None
  has_changed = False
  with open(fn, "r") as fd:
    soup = BeautifulSoup(fd)

    for tag in soup.select("div#" + DIV_ID):
      tag.extract()
      has_changed = True

  if has_changed:
    with codecs.open(fn, "w", "utf-8") as fd:
      fd.write(unicode(soup))


def MarkOne(fn, note, link):
  soup = None
  with open(fn, "r") as fd:
    soup = BeautifulSoup(fd)

    # Check if the document is already marked.
    if len(soup.select("div#" + DIV_ID)) > 0:
      logging.warning("Document '%s' is already marked.", fn)
      return

    # Build the box containing the note.
    note_div = soup.new_tag("div")
    note_div["id"] = DIV_ID
    note_div["style"] = DIV_STYLE

    note_header = soup.new_tag("p")
    note_header["style"] = HEADER_STYLE
    note_header.string = "Note:"
    note_div.append(note_header)

    note_main = soup.new_tag("p")
    note_main["style"] = NOTE_STYLE
    note_div.append(note_main)

    note_text = soup.new_string(note + " ")
    note_main.append(note_text)

    note_link = soup.new_tag('a')
    note_link["href"] = link
    note_link.string = "Goto the latest version"
    note_main.append(note_link)

    note_final_dot = soup.new_string(".")
    note_main.append(note_final_dot)

    # Selector should lead to a single node.
    done = False
    for selector in SELECTORS:
      node_lst = soup.select(selector)
      if not done and len(node_lst) == 1:
        node_lst[0].insert_after(note_div)
        done = True

    if not done:
      if soup.body:
        soup.body.insert(0, note_div)
      else:
        raise Exception("Unable to find a place to insert note in '%s'." %
                        fn)

  with codecs.open(fn, "w", "utf-8") as fd:
    fd.write(unicode(soup))

def main():
  # Parse command line.
  parser = OptionParser()
  parser.add_option('-v', '--log', dest='loglevel',
                    help='set the log level')
  parser.add_option('--unset', action='store_false', dest='do_mark',
                    default=True, help='just remove the notification boxes')
  parser.add_option('--exclude', dest='exclude',
                    help='set exclude pattern')
  parser.add_option('--text', dest='text',
                    help='set the text to display in the note')
  parser.add_option('--link', dest='link',
                    help='link to this page')

  (options, args) = parser.parse_args()

  if options.loglevel:
    logging.basicConfig(level=getattr(logging, options.loglevel.upper()))

  exclude_regex = None
  if options.exclude:
    exclude_regex = re.compile(options.exclude)

  if options.do_mark:
    if not options.link:
      raise Exception("No link defined.")

    if not options.text:
      raise Exception("No text defined.")

  # Apply transformation to input file.
  for fn in args:
    # Skip files that match.
    if exclude_regex and exclude_regex.match(os.path.basename(fn)):
      logging.info("Skipping file '%s'", fn)
      continue

    UnMarkOne(fn)
    if options.do_mark:
      MarkOne(fn, options.text, options.link)

if __name__ == '__main__':
  main()

