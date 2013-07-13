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

# Max cache age.
MAX_CACHE_AGE = 60

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

def CacheForgeHTML(page_url, online, cache_dir):
  """Download the URL if necessary otherwise just use the cache."""

  html_fn = os.path.join(cache_dir, 'scrape.html')
  html_exists = os.path.exists(html_fn)
  html_download = False
  if html_exists:
    # Test if the file is old.
    st = os.stat(html_fn)
    mtime = st.st_mtime
    file_age = time.time() - mtime
    if MAX_CACHE_AGE < file_age:
      if online:
        logging.info("The file '%s' is %d seconds old, redownloading.",
                     html_fn, file_age)
        html_download = True
      else:
        logging.info("The file '%s' is %d seconds old " +
                     "but not online, so no redownload.",
                     html_fn, file_age)
    else:
      logging.info("The file '%s' is recent enough.", html_fn)
  else:
    logging.info("The file '%s' doesn't exist, downloading.")
    html_download = True

  if html_download:
    download_ok = False
    with open(html_fn, "wb") as fp:
      curl = pycurl.Curl()
      curl.setopt(pycurl.URL, page_url)
      curl.setopt(pycurl.FOLLOWLOCATION, 1)
      curl.setopt(pycurl.MAXREDIRS, 5)
      curl.setopt(pycurl.CONNECTTIMEOUT, 30)
      curl.setopt(pycurl.TIMEOUT, 300)
      curl.setopt(pycurl.NOSIGNAL, 1)
      curl.setopt(pycurl.WRITEDATA, fp)
      try:
          curl.perform()
          logging.info("Download of '%s' done.", page_url)
          download_ok = True
      except:
          import traceback
          traceback.print_exc(file=sys.stderr)
      curl.close()

    if not download_ok:
      os.remove(html_fn)
      raise Error("Not able to download '%s'" % page_url)

  return html_fn

def main():
  # Parsing command line.
  parser = OptionParser()
  parser.add_option('-c', '--cache_dir', dest='cache_dir',
                    help='store data to DIRNAME')
  parser.add_option('-p', '--forge_page', dest='forge_page',
                    help='forge page to scrape.')
  parser.add_option('-z', '--online', dest='online',
                    help='wether we are online.')
  parser.add_option('-i', '--input', dest='input_filename',
                    help='read data from FILENAME')
  parser.add_option('-o', '--output', dest='output_filename',
                    help='write data to FILENAME')
  parser.add_option('-v', '--log', dest='loglevel',
                    help='set the log level')
  (options, args) = parser.parse_args()

  if options.loglevel:
    logging.basicConfig(level=getattr(logging, options.loglevel.upper()))

  online = True
  if options.online is "false":
    online = False
  logging.info("Online: %s", online)

  if not options.cache_dir:
    raise Error('You need to specify a cache directory (--cache_dir).')

  if not options.forge_page:
    raise Error('You need to specify a forge page (--forge_page).')

  if not options.input_filename:
    raise Error('You need to specify an input filename (--input).')

  # Download the forge page if necessary.
  forge_page_fn = CacheForgeHTML(options.forge_page, online, options.cache_dir)

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
