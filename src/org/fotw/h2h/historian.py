"""
Historian is a class that tracks event dates for a given pair of people.
"""

from src.org.fotw.h2h.h2h_pb2 import MatchingHistory, MatchSet, Match

from collections import defaultdict
import copy
import datetime


_TEXTPROTO_DATE_FORMAT = '%Y%m%d'


def from_proto(matching_history):
  h = Historian()
  for match_set in matching_history.match_set:
    try:
      event_date = datetime.datetime.strptime(match_set.date_yyyymmdd, _TEXTPROTO_DATE_FORMAT)
    except ValueError:
      raise Exception('failed to parse match date %s' % match_set.date_yyyymmdd)
    for match in match_set.match:
      if match.host:
          h.push_host_date(match.host, match.member, event_date)
      else:
        h.push_hostless_date(match.member, event_date)
  return h


class TwoLevelDateDictionary():
  def __init__(self):
    # self._d[a][b] is a sorted list of dates
    self._d = {}
  
  def keys(self):
    return self._d.keys()
  
  def l2_keys(self, a):
    if a not in self._d:
      return []  # getters should not modify.
    return self._d[a].keys()

  def get_event_dates(self, a, b):
    if a not in self._d:
      return []  # getters should not modify.
    if b not in self._d[a]:
      return []  # getters should not modify.
    return self._d[a][b]

  def push_event_date(self, a, b, event_date):
    if a not in self._d:
      self._d[a] = {}
    if b not in self._d[a]:
      self._d[a][b] = []

    mut_date_list = self._d[a][b]
    if event_date not in mut_date_list:
      mut_date_list.append(event_date)
    mut_date_list.sort()

  def pop_event_date(self, a, b, event_date):
    if a not in self._d:
      raise ValueError('pop from empty list')
    if b not in self._d[a]:
      raise ValueError('pop from empty list')

    mut_date_list = self._d[a][b]
    if event_date not in mut_date_list:
      raise ValueError('event date to remove is not present')
    mut_date_list.remove(event_date)


class Historian():
  def __init__(self):
    # self._host_dates[a][b] returns the list of times that a has hosted b
    self._host_dates = TwoLevelDateDictionary()

    # self._hostless_dates[a][b] returns the list of times that a has met with b
    # and there was no host. In this dictionary, ordering doesn't
    # matter so self._hostless_dates[a][b] = self._hostless_dates[b][a]    
    self._hostless_dates = TwoLevelDateDictionary()

    # self._meet_dates[a][b] returns the list of times that a has met with b
    # independent of whether a was hosting b. In this dictionary, ordering doesn't
    # matter so self._meet_dates[a][b] = self._meet_dates[b][a]    
    # Note: self._meet_dates also includes self._host_dates
    self._meet_dates = TwoLevelDateDictionary()

  def get_past_host_names(self):
    return self._host_dates.keys()

  def get_all_names(self):
    name_set = set()
    for a in self._meet_dates.keys():
      name_set.add(a)
      for b in self._meet_dates.l2_keys(a):
        name_set.add(b)

    return name_set

  def get_host_dates(self, a, b):
    return self._host_dates.get_event_dates(a, b)

  def push_host_date(self, host, members, event_date):
    for member in members:
      if member == host:
        continue
      self._meet_dates.push_event_date(host, member, event_date)
      self._meet_dates.push_event_date(member, host, event_date)

      self._host_dates.push_event_date(host, member, event_date)

  def pop_host_date(self, host, members, event_date):
    for member in members:
      if member == host:
        continue
      self._meet_dates.pop_event_date(host, member, event_date)
      self._meet_dates.pop_event_date(member, host, event_date)

      self._host_dates.pop_event_date(host, member, event_date)

  def push_hostless_date(self, group, event_date):
    for a in group:
      for b in group:
        if a == b:
          continue
        self._meet_dates.push_event_date(a, b, event_date)
        self._hostless_dates.push_event_date(a, b, event_date)


  def pop_hostless_date(self, group, event_date):
    for a in group:
      for b in group:
        if a == b:
          continue
        self._meet_dates.pop_event_date(a, b, event_date)
        self._hostless_dates.pop_event_date(a, b, event_date)

  def get_meetup_dates(self, a, b):
    return self._meet_dates.get_event_dates(a, b)

  def get_past_guests(self, a):
    return self._host_dates.l2_keys(a)

  def get_past_associates(self, a):
    return self._meet_dates.l2_keys(a)

  def to_proto(self):
    date_to_host_to_guests = defaultdict(lambda: defaultdict(set))
    date_to_hostless_gatherings = defaultdict(set)

    for a in sorted(self._host_dates.keys()):
      for b in self._host_dates.l2_keys(a):
        if b == a:
          continue
        for event_date in self.get_host_dates(a, b):
          date_to_host_to_guests[event_date][a].add(a)
          date_to_host_to_guests[event_date][a].add(b)

    for a in self._hostless_dates.keys():
      for b in self._hostless_dates.l2_keys(a):
        for event_date in self._hostless_dates.get_event_dates(a, b):
          date_to_hostless_gatherings[event_date].add((a, b))

    matching_history = MatchingHistory()
    all_event_dates = set(list(date_to_host_to_guests.keys()) + list(date_to_hostless_gatherings.keys()))
    for event_date in sorted(all_event_dates):
      match_set = matching_history.match_set.add()
      match_set.date_yyyymmdd = event_date.strftime(_TEXTPROTO_DATE_FORMAT)

      if event_date in date_to_host_to_guests:
        for host in sorted(date_to_host_to_guests[event_date].keys()):
          match = match_set.match.add()
          match.host = host
          del match.member[:]  # Or potentially match.ClearField('member')
          match.member.extend(sorted(date_to_host_to_guests[event_date][host]))
      
      if event_date in date_to_hostless_gatherings:
        hostless_groups = []
        name_to_group_index = {}
        for (a, b) in date_to_hostless_gatherings[event_date]:
          if a in name_to_group_index:
            hostless_groups[name_to_group_index[a]].add(b)
            name_to_group_index[b] = name_to_group_index[a]
          elif b in name_to_group_index:
            hostless_groups[name_to_group_index[b]].add(a)
            name_to_group_index[a] = name_to_group_index[b]
          else:
            hostless_groups.append(set([a, b]))
            name_to_group_index[a] = len(hostless_groups) - 1
            name_to_group_index[b] = name_to_group_index[a]

        hostless_groups.sort(key=lambda group: min(group))
        for hostless_group in hostless_groups:
          match = match_set.match.add()
          del match.member[:]  # Or potentially match.ClearField('member')
          match.member.extend(sorted(hostless_group))
    
    return matching_history
