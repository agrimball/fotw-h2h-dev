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


# Respected in gen_match_config
MAX_GUEST_COUNT = 2


Participant = collections.namedtuple(
    'Participant',
    ['name', 'is_family', 'residence', 'participating', 'can_host',
     'child_count'])
Match = collections.namedtuple(
    'Match', ['hosts', 'guests'])


def parse_participant_csv(p_csv_file):
  """Outputs a dictionary from participant name to properties."""
  is_first_row = True
  p_config = {}
  for row in csv.reader(p_csv_file):
    if is_first_row:
      is_first_row = False
      continue

    num_children = int(row[5] or 0)
    p = Participant(
        name=row[0],
        is_family=(row[1] == 'Y'),
        residence=row[2],
        participating=(row[3] == 'Y'),
        can_host=(row[4] == 'Y'),
        child_count=num_children)
    p_config[p.name] = p
  return p_config


def validate_inputs(p_info, host_historian):
  """Raises an error if inputs are malformed in any way."""
  p_name_set = set([name for name in p_info])
  for name in p_info:
    p = p_info[name]

  for a in host_historian.get_all_names():
    if a not in p_name_set:
      raise Exception('unknown host name from textproto: ' + a)


def push_match_config(host_historian, match_config, match_date):
  """Updates the host info dictionaries given a match config."""
  for match in match_config:
    # Update host_info
    for host in match.hosts:
      for guest in match.guests:
        host_historian.push_event_date(host, guest, match_date)


def pull_match_config(host_historian, match_config):
  for match in match_config:
    # Update host_info
    for host in match.hosts:
      for guest in match.guests:
        host_historian.pop_event_date(host, guest)


def get_rel_dev_score(a, b, host_historian):
    meet_count_i_j = len(
        host_historian.get_event_dates(a, b)
        + host_historian.get_event_dates(b, a))
    return meet_count_i_j ** 2


def get_host_service_score(host, p_info, host_historian, match_date):
  if not p_info[host].can_host:
    return 0
  return get_info_score(host, host_historian, match_date)


def get_info_score(a, h, match_date):
  most_recent_time = datetime.datetime.min
  total_count = 0

  for b in h.get_associates(a):
    event_dates = h.get_event_dates(a, b)
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


def gen_match_config(p_config):
  """Returns (matches, found_match) for a given participant config."""
  p_names = [p_name for p_name in p_config if p_config[p_name].participating]
  random.shuffle(p_names)  # Shuffles in-place.

  # matches: [([host1, host2], [guest1, guest2]), ...]
  matches = []
  i = 0
  while i < len(p_names):
    # Starting with this participant, figure out how many can co-host.
    # Constraint: hosts must live at same residence.
    possible_cohost_len = 1
    while (
        i + possible_cohost_len < len(p_names)
        and (
            p_config[p_names[i+possible_cohost_len]].residence ==
            p_config[p_names[i]].residence
            )
        ):
      possible_cohost_len += 1
    # Randomly choose the number that will host together.
    n_hosts = random.randint(1, possible_cohost_len)
    host_names = p_names[i:i+n_hosts]
    i += n_hosts

    # Check that we're respecting the and can_host bits.
    if not p_config[host_names[0]].can_host:
      return None, False

    if i >= len(p_names):
      return None, False

    # p_names[i] is now the first guest participant. Figure out how many
    # co-guests are possible.
    # Constraint: at most one family, no large families with singles..
    possible_coguest_len = 1
    has_family = p_config[p_names[i]].is_family
    has_singles = not has_family
    while (
        i + possible_coguest_len < len(p_names)
        and not (
            (has_family and p_config[p_names[i+possible_coguest_len]].is_family)
            or (has_singles and p_config[p_names[i+possible_coguest_len]].child_count >= 5)
            )
        ):
      has_family = (
          has_family or p_config[p_names[i+possible_coguest_len]].is_family)
      has_singles = (
          has_singles or (not p_config[p_names[i+possible_coguest_len]].is_family))
      possible_coguest_len += 1
    # Randomly choose the number that will guest together.
    n_guests = random.randint(1, min(possible_coguest_len, MAX_GUEST_COUNT))
    guest_names = p_names[i:i+n_guests]
    i += n_guests

    matches.append(
        Match(hosts=host_names, guests=guest_names))
  return matches, True


def get_best_match_config(
    p_info, host_historian, match_date, n):
  max_score = None
  best_match_config = None
  for _ in range(n):
    match_config, found_match = gen_match_config(p_info)
    while not found_match:
      match_config, found_match = gen_match_config(p_info)
    push_match_config(
        host_historian, match_config, match_date)
    match_config_score = get_match_config_score(
      p_info, host_historian, match_date)
    pull_match_config(
        host_historian, match_config)
    if max_score is None or match_config_score > max_score:
      max_score = match_config_score
      best_match_config = match_config
  return best_match_config


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
      host_historian = historian.parse_from_textproto_str(host_textproto_file.read())
      validate_inputs(p_info, host_historian)

      best_match_config = get_best_match_config(
        p_info, host_historian, match_date, int(args.N))

      push_match_config(
          host_historian, best_match_config, match_date)
      with open(args.updated_host_textproto_path, 'w') as out_file:
        print(host_historian.write_to_textproto_str(), file=out_file)
      for match in best_match_config:
        print(match)
      for warning in history_warnings.get_warnings(host_historian):
        print(warning)


if __name__ == '__main__':
  main(sys.argv)

