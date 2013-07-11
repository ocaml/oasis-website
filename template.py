#!/usr/bin/python

from mako.template import Template
import simplejson as json
from optparse import OptionParser

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
  (options, args) = parser.parse_args()

  if not options.cache_dir:
    raise Error('You need to specify a cache directory (--cache_dir).')

  if not options.forge_page:
    raise Error('You need to specify a forge page (--forge_page).')

  online = True
  if options.online is "false":
    online = False

  if not options.input_filename:
    raise Error('You need to specify an input filename (--input).')

  # TODO: take care of cache_dir/forge_page/online options.

  data = dict()
  with file('scrape.json', 'r') as fd:
    data = json.load(fd)
  mytemplate = Template(filename=options.input_filename)
  output = mytemplate.render(data=data)
  if options.output_filename:
    with file(options.output_filename, 'w') as fd:
      fd.write(output)
  else:
    print output

if __name__ == '__main__':
  main()
