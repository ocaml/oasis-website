#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from mako.template import Template

import logging
import re
import os
import pycurl
import time
import common
import zipfile
import StringIO
import sys

FAQ_URL = 'https://docs.google.com/document/d/1uPm45WHr8paD27IM0QhVLHr0SS0mupANMskD1BXrvCI/export?format=zip&id=1uPm45WHr8paD27IM0QhVLHr0SS0mupANMskD1BXrvCI&token=AC4w5VgArQew9BvfyTJaePflHvQrKcXbtA%3A1373999475840'

def dumpFile(comment, fn, fd):
  if not fn:
    return
  with open(fn) as fd2:
    print >>fd, '<!-- %s -->' % comment
    for i in fd2:
      print >>fd, i.rstrip()

def main():
  # Parse command line.
  parser = common.CreateOptionsParser()
  parser.add_option('-o', '--output', dest='output_filename',
                    help='write data to FILENAME')
  parser.add_option('-H', '--part-header', dest='part_header')
  parser.add_option('-B', '--part-before-body', dest='part_before_body')
  parser.add_option('-A', '--part-after-body', dest='part_after_body')
  parser.add_option('--css', dest='css')
  options = common.ApplyOptionsParser(parser)

  # Download the zip file.
  zip_fn = common.CacheCurl("FAQ.zip",
                            FAQ_URL,
                            options.online,
                            options.cache_dir)

  # Extract FAQ.html.
  with zipfile.ZipFile(zip_fn) as z:
    with z.open('FAQ.html') as fd:
      out = sys.stdout
      if options.output_filename:
        out = StringIO.StringIO()

      # Extract data from the HTML file.
      soup = BeautifulSoup(fd)
      title = soup.find('title')
      body = soup.find('body')
      style = soup.find('style')

      print >>out, """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="generator" content="googledoc.py" />
  <meta name="author" content="author Sylvain Le Gall" />
  %s
  %s
""" % (title, style.prettify())
      if options.css:
        print >>out, """
  <link rel="stylesheet" href="%s" type="text/css" />
""" % options.css
      dumpFile('part_header', options.part_header, out)
      print >>out, """
</head>
<body>
"""
      dumpFile('part_before_body', options.part_before_body, out)
      print >>out, """
<!-- body -->
"""
      for i in soup.body:
        print >>out, i.prettify()
      dumpFile('part_after_body', options.part_after_body, out)
      print >>out, """
</body>
</html>
"""
      if options.output_filename:
        with open(options.output_filename, 'w') as real_out:
          print >>real_out, out.getvalue()
        out.close()


if __name__ == '__main__':
  main()
