#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from mako.template import Template
from optparse import OptionParser
from urlparse import urljoin

import logging
import re
import os
import pycurl
import time
import common

# Regexp to extract data from URL found in the download page.
LINK_RE = re.compile(r'^.*/(?P<product>.+)-(?P<version>.+)\.tar\.gz$')

class ForgeProduct(object):
  """A product."""

  def __init__(self, name):
    self.name = name
    self.latest = None
    self.others = []

  def __repr__(self):
    return ('name: %s;\nlatest: {%r};\nothers: {%s};\n' %
            (self.name, self.latest,
              ';\n'.join(['%r' % i for i in self.others])))


class ForgeVersion(object):
  """A specific version of a product."""

  def __init__(self, url, version):
    self.url = url
    self.version = version

  def __repr__(self):
    return ('url: %s; version: %s' % (self.url, self.version))


def ParseForgeHTML(page_fn, page_url):
  """Go through a forge HTML page and extract data."""

  with open(page_fn, "r") as fd:
    soup = BeautifulSoup(fd)
    products = dict()
    for link in [a['href'] for a in soup.findAll('a')]:
      m = LINK_RE.match(link)
      if m:
        forge_version = ForgeVersion(urljoin(page_url, link),
                                     m.group('version'))

        product_name = m.group('product')
        if product_name not in products:
          forge_product = ForgeProduct(product_name)
          forge_product.latest = forge_version
          products[product_name] = forge_product
        else:
          products[product_name].others.append(forge_version)
    return products


def main():
  # Parsing command line.
  parser = common.CreateOptionsParser()
  parser.add_option('-p', '--forge_page', dest='forge_page',
                    help='forge page to scrape.')
  parser.add_option('-i', '--input', dest='input_filename',
                    help='read data from FILENAME')
  parser.add_option('-o', '--output', dest='output_filename',
                    help='write data to FILENAME')
  options = common.ApplyOptionsParser(parser)

  if not options.forge_page:
    raise Error('You need to specify a forge page (--forge_page).')

  if not options.input_filename:
    raise Error('You need to specify an input filename (--input).')

  # Download the forge page if necessary.
  forge_page_fn = common.CacheCurl('scrape.html',
                                   options.forge_page,
                                   options.online,
                                   options.cache_dir)

  # Parse the forge page.
  data = ParseForgeHTML(forge_page_fn, options.forge_page)
  oasis = data['oasis']
  oasis_doc = data['oasis-doc']

  # Render the template.
  mytemplate = Template(filename=options.input_filename)
  output = mytemplate.render(oasis=data['oasis'], oasis_doc=data['oasis-doc'])
  if options.output_filename:
    with file(options.output_filename, 'w') as fd:
      fd.write(output)
  else:
    print output

if __name__ == '__main__':
  main()
