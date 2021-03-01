# Takes an old hosting CSV file and outputs the same file in textproto format.
# Output proto is h2h.proto's MatchingHistory

import argparse
import sys

from src.org.fotw.h2h import historian

def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input_csv_path',
      required=True,
      help='input csv file location')
  parser.add_argument(
      '--output_textproto_path',
      required=True,
      help='output textproto file location')
  args = parser.parse_args(args=argv[1:])

  with open(args.input_csv_path, 'r') as input_csv_file:
    host_historian = historian.parse_from_csv_str(input_csv_file.read())
    with open(args.output_textproto_path, 'w') as out_file:
      print(host_historian.write_to_textproto_str(), file=out_file)


if __name__ == '__main__':
  main(sys.argv)

