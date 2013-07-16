# Common functions and definitions.

from optparse import OptionParser

import logging
import os
import pycurl
import time

# Max cache age.
MAX_CACHE_AGE = 60


def CreateOptionsParser():
  """Return a parser for command line with common options."""
  parser = OptionParser()
  parser.add_option('-c', '--cache_dir', dest='cache_dir',
                    help='store data to DIRNAME')
  parser.add_option('-z', '--online', dest='online',
                    help='wether we are online.')
  parser.add_option('-v', '--log', dest='loglevel',
                    help='set the log level')
  return parser


def ApplyOptionsParser(parser):
  """Apply a parser created with CreateOptionsParser."""
  (options, args) = parser.parse_args()

  if options.loglevel:
    logging.basicConfig(level=getattr(logging, options.loglevel.upper()))

  online = True
  if options.online is "false":
    online = False
  logging.info("Online: %s", online)
  options.online = online

  if not options.cache_dir:
    raise Error('You need to specify a cache directory (--cache_dir).')

  return options


def CacheCurl(base_fn, page_url, online, cache_dir):
  """Download an URL if possible and needed."""
  html_fn = os.path.join(cache_dir, base_fn)
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
    logging.info("The file '%s' doesn't exist, downloading.", html_fn)
    html_download = True

  if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

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
