"""
Historian is a class that tracks event dates for a given pair of people.
"""

from src.org.fotw.h2h.h2h_pb2 import MatchingHistory, MatchSet, Match
from com_google_protobuf_python_srcs.python.google.protobuf import text_format

from collections import defaultdict
import copy
import csv
import datetime


_CSV_DATE_FORMAT = '%m/%d/%Y'
_TEXTPROTO_DATE_FORMAT = '%Y%m%d'


def parse_from_csv_str(csv_str):
  """Resets the data structure & sets it to the CSV string."""
  h = Historian()

  is_first_row = True
  first_row = []
  for row in csv.reader(csv_str.split('\n')):
    # Read & validate the first row.
    if is_first_row:
      first_row = list(row)
      is_first_row = False

      for i in range(1, len(first_row)):
        if not first_row[i]:
          raise Exception('empty guest name in first row at index %d' % i)
      continue

    if not row:
      break

    a_name = row[0]
    for col_idx in range(1, len(row)):
      if col_idx >= len(first_row):
        break  # If there's exta values beyond the first row, just ignore.
      b_name = first_row[col_idx]
      cell_val = row[col_idx]
      parts = cell_val.split('--')
      if len(parts) == 1 and (parts[0] == 'X' or not parts[0]):
        continue
      for part in parts:
        try:
          event_date = datetime.datetime.strptime(part, _CSV_DATE_FORMAT)
        except ValueError:
          raise Exception('failed to parse %s' % cell_val)
        h.push_event_date(a_name, b_name, event_date)
  return h


def from_dict(d):
  """Resets the data structure & sets it to the dictionary value."""
  if not isinstance(d, dict):
    raise ValueError('from_dict with non-dict')
  h = Historian()
  for a in d:
    if not isinstance(d[a], dict):
      raise ValueError('from_dict[key] is not dict')
    for b in d[a]:
      if not isinstance(d[a][b], list):
        raise ValueError('from_dict[key][key] is not list')
      for event_date in d[a][b]:
        if not isinstance(event_date, datetime.datetime):
          raise ValueError('from_dict[key][key] entry is not datetime.datetime')
        h.push_event_date(a, b, event_date)
  return h


def parse_from_textproto_str(textproto_str):
  matching_history = MatchingHistory()
  text_format.Parse(textproto_str, matching_history)
  h = Historian()
  for match_set in matching_history.match_set:
    try:
      event_date = datetime.datetime.strptime(match_set.date_yyyymmdd, _TEXTPROTO_DATE_FORMAT)
    except ValueError:
      raise Exception('failed to parse match date %s' % match_set.date_yyyymmdd)
    for match in match_set.match:
      if not match.host:
        raise Exception('historian does not yet understand gatherings without hosts')
      for member in match.member:
        h.push_event_date(match.host, member, event_date)
  return h


class Historian():
  def __init__(self):
    # {'a': {'b': [firstDate, secondDate, ...]}}
    self._event_dates = {}

  def get_primary_names(self):
    return self._event_dates.keys()

  def get_all_names(self):
    name_set = set()
    for a in self._event_dates:
      name_set.add(a)
      for b in self.get_associates(a):
        name_set.add(b)

    return name_set

  def get_event_dates(self, a, b):
    if a not in self._event_dates:
      return []  # getters should not modify.
    if b not in self._event_dates[a]:
      return []  # getters should not modify.
    return self._event_dates[a][b]

  def push_event_date(self, a, b, event_date):
    if a not in self._event_dates:
      self._event_dates[a] = {}
    if b not in self._event_dates[a]:
      self._event_dates[a][b] = []

    mutable_dates = self._event_dates[a][b]
    if not mutable_dates:
      mutable_dates.append(event_date)
    else:
      # Ensure that the list is always sorted in ascending order.
      last_event_date = mutable_dates[len(mutable_dates) - 1]
      mutable_dates.append(event_date)

      # Because the rest of the list is sorted, we only need to check that
      # event_date isn't before the previous last_event_date. If it is, then we
      # simply re-sort the list to ensure that it finds its place.
      if event_date < last_event_date:
        mutable_dates.sort()

  def pop_event_date(self, a, b):
    if a not in self._event_dates:
      raise ValueError('pop from empty list')
    if b not in self._event_dates[a]:
      raise ValueError('pop from empty list')
    self._event_dates[a][b].pop()

  def get_associates(self, a):
    if a not in self._event_dates:
      return []  # getters should not modify.
    return self._event_dates[a].keys()

  def write_to_csv_str(self, top_left_cell_value):
    sorted_names = sorted(self.get_all_names())

    csv_lines = [','.join([top_left_cell_value] + sorted_names)]
    for a in sorted_names:
      a_row = [a]
      for b in sorted_names:
        if b == a:
          cell_value = 'X'
        elif not self.get_event_dates(a, b):
          cell_value = ''
        else:
          event_dates = self.get_event_dates(a, b)
          cell_value = '--'.join([d.strftime(_CSV_DATE_FORMAT) for d in event_dates])
        a_row.append(cell_value)
      csv_lines.append(','.join(a_row))
    return '\n'.join(csv_lines)

  def to_dict(self):
    return copy.deepcopy(self._event_dates)

  def write_to_textproto_str(self):
    date_to_host_to_guests = defaultdict(lambda: defaultdict(set))
    sorted_names = sorted(self.get_all_names())

    for a in sorted_names:
      for b in sorted_names:
        if b == a:
          continue
        for event_date in self.get_event_dates(a, b):
          dateyyyymmdd = event_date.strftime(_TEXTPROTO_DATE_FORMAT)
          date_to_host_to_guests[dateyyyymmdd][a].add(a)
          date_to_host_to_guests[dateyyyymmdd][a].add(b)

    matching_history = MatchingHistory()
    for date in sorted(date_to_host_to_guests.keys()):
      match_set = matching_history.match_set.add()
      match_set.date_yyyymmdd = date
      for host in sorted(date_to_host_to_guests[date].keys()):
        match = match_set.match.add()
        match.host = host
        del match.member[:]  # Or potentially match.ClearField('member')
        match.member.extend(sorted(date_to_host_to_guests[date][host]))
    return text_format.MessageToString(matching_history)
