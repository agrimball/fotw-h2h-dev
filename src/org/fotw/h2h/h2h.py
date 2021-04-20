"""Generates an h2h match monte-carlo style.

Idea: Randomly generate N match configs & score them.
At the end, show the best match config.


TODOs:
 - Copy-paste-able match output.
 - Ability to run multiple scoring algos & record best match + scoring for each
 - Better hosting load-balancing:
  -- extra_effort = (num_guests / normal_people_host_cooks_for)
  -- long-term measure: SUM(extra_effort) / (time since joined h2h)
  -- short-term measure: total extra_effort in past 2 months / MIN(2 months, time since joined h2h)
 - More debuggable output:
  -- score + score breakdown by metric (rel dev, hosting fairness)
  -- view rel dev, hosting fairness fairness max & min values.

Inputs:
h2h participant CSV
h2h previous matches textproto file

Outputs:
updated h2h matches textproto file


Scoring: Load-balanced hosting, then relationship development.
"""

import argparse
import collections
import csv
import datetime
import math
import random
import sys

from src.org.fotw.h2h import historian
from src.org.fotw.h2h import history_warnings
from src.org.fotw.h2h import match_generator
from src.org.fotw.h2h.h2h_pb2 import MatchingHistory

from com_google_protobuf_python_srcs.python.google.protobuf import text_format

Participant = collections.namedtuple(
    'Participant',
    ['name', 'is_family', 'participating', 'can_host',
     'child_count', 'gender_if_single'])


def parse_participant_csv(p_csv_file):
  """Outputs a dictionary from participant name to properties."""
  is_first_row = True
  p_config = {}
  for row in csv.reader(p_csv_file):
    if is_first_row:
      is_first_row = False
      continue

    num_children = int(row[4] or 0)
    p = Participant(
        name=row[0],
        is_family=(row[1] == 'Y'),
        participating=(row[2] == 'Y'),
        can_host=(row[3] == 'Y'),
        child_count=num_children,
        gender_if_single=row[5])
    p_config[p.name] = p
  return p_config


def validate_inputs(p_info, host_historian):
  """Raises an error if inputs are malformed in any way."""
  p_name_set = set([name for name in p_info])
  for name in p_info:
    p = p_info[name]
    if not p.is_family and p.gender_if_single not in ['M','F']:
      raise ValueError('no gender for single participant: ' + name)    

  for a in host_historian.get_all_names():
    if a not in p_name_set:
      raise Exception('unknown host name from textproto: ' + a)


def push_match_config(host_historian, match_config, match_date):
  """Updates the host info dictionaries given a match config."""
  for match in match_config.match:
    if match.host:
      host_historian.push_host_date(match.host, match.member, match_date)
    else:
      host_historian.push_hostless_date(match.member, match_date)


def pop_match_config(host_historian, match_config, match_date):
  for match in match_config.match:
    if match.host:
      host_historian.pop_host_date(match.host, match.member, match_date)
    else:
      host_historian.pop_hostless_date(match.member, match_date)


def get_rel_dev_score(a, b, host_historian):
    meet_count_i_j = len(host_historian.get_meetup_dates(a, b))
    return meet_count_i_j ** 2


def get_host_service_score(host, p_info, host_historian, match_date):
  if not p_info[host].can_host:
    return 0
  return get_info_score(host, host_historian, match_date)


def get_info_score(a, h, match_date):
  most_recent_time = datetime.datetime.min
  total_count = 0

  for b in h.get_past_guests(a):
    event_dates = h.get_host_dates(a, b)
    if not event_dates:
      continue
    last_time = event_dates[len(event_dates) - 1]
    count = len(event_dates)
    total_count += count
    if last_time > most_recent_time:
      most_recent_time = last_time
  freq_badness = (match_date - most_recent_time).days
  effort_badness = total_count
  return 0 - freq_badness - effort_badness


def get_match_config_score(p_info, host_historian, match_date):
  """Scores a match configuration."""
  # balance relationship development
  rel_dev_badness = 0
  name_list = [name for name in p_info]
  i = 0
  while i < len(name_list):
    j = i+1
    while j < len(name_list):
      rel_dev_badness += get_rel_dev_score(name_list[i], name_list[j], host_historian)
      j += 1
    i += 1
  rel_dev_badness = math.sqrt(rel_dev_badness)

  host_service_score = sum([
    get_host_service_score(host, p_info, host_historian, match_date)
    for host in name_list
  ])

  return (
      (1e6 * host_service_score) -
      min(rel_dev_badness, 1e6)
  )


def get_best_match_config(
    p_info, host_historian, match_date, n):
  max_score = None
  best_match_config = None
  failed_match_generations = 0
  for _ in range(n):
    match_config, found_match = match_generator.gen_match_config(match_date, p_info)
    while not found_match:
      match_config, found_match = match_generator.gen_match_config(match_date, p_info)
      failed_match_generations += 1
    push_match_config(
        host_historian, match_config, match_date)
    match_config_score = get_match_config_score(
      p_info, host_historian, match_date)
    pop_match_config(
        host_historian, match_config, match_date)
    if max_score is None or match_config_score > max_score:
      max_score = match_config_score
      best_match_config = match_config
  return best_match_config, failed_match_generations


def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--participants_csv_path',
      required=True,
      help='participants csv file location')
  parser.add_argument(
      '--host_textproto_path',
      required=True,
      help='hosting textproto file location')
  parser.add_argument(
      '--updated_host_textproto_path',
      required=True,
      help='updated hosting textproto file location')
  parser.add_argument(
      '--match_date',
      required=True,
      help='date for next h2h meetup. Format: yyyy-mm-dd')
  parser.add_argument(
      '--N',
      required=True,
      help='total random valid configs to generate & evaluate')
  args = parser.parse_args(args=argv[1:])

  match_date = datetime.datetime.strptime(args.match_date, '%Y-%m-%d')
  with open(args.participants_csv_path, 'r') as p_csv_file:
    with open(args.host_textproto_path, 'r') as host_textproto_file:
      p_info = parse_participant_csv(p_csv_file)
      matching_history = MatchingHistory()
      text_format.Parse(host_textproto_file.read(), matching_history)
      host_historian = historian.from_proto(matching_history)
      validate_inputs(p_info, host_historian)

      best_match_config, failed_match_generations = get_best_match_config(
        p_info, host_historian, match_date, int(args.N))
      print('failed match generations: %d' % failed_match_generations)

      push_match_config(
          host_historian, best_match_config, match_date)
      with open(args.updated_host_textproto_path, 'w') as out_file:
        print(text_format.MessageToString(host_historian.to_proto()), file=out_file)
      for match in best_match_config.match:
        if match.host:
          print(match.host + ': ' + ', '.join([m for m in match.member if m != match.host]))
        else:
          print('hostless: ' + ', '.join(match.member))
      for warning in history_warnings.get_warnings(host_historian):
        print(warning)


if __name__ == '__main__':
  main(sys.argv)

