#!/usr/bin/python

from mako.template import Template
import simplejson as json
from optparse import OptionParser

def main():
  # Parsing command line.
  parser = OptionParser()
  parser.add_option('-i', '--input', dest='input_filename',
                    help='read data from FILENAME')
  parser.add_option('-d', '--data', dest='data_filename',
                    help='read JSON data from FILENAME')
  parser.add_option('-o', '--output', dest='output_filename',
                    help='write data to FILENAME')
  (options, args) = parser.parse_args()

  if not options.data_filename:
    raise Error('You need to specify a data filename (--data).')

  if not options.input_filename:
    raise Error('You need to specify an input filename (--input).')

  data = dict()
  with file(options.data_filename, 'r') as fd:
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
