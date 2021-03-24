from src.org.fotw.h2h.h2h_pb2 import MatchSet, Match

import random


_MAX_GUEST_COUNT = 2
_MIN_SINGLES_GROUP_SIZE = 3
_MAX_SINGLES_GROUP_SIZE = 4


def gen_match_config(match_date, p_config):
  """
  Returns (matches, found_match) for a given participant config.

  match_date is assumed to be a datetime.datetime object
  """
  p_names = [p_name for p_name in p_config if p_config[p_name].participating]
  random.shuffle(p_names)  # Shuffles in-place.

  match_set = MatchSet(date_yyyymmdd=match_date.strftime('%Y%m%d'))
  i = 0
  while i < len(p_names):
    first_p_name = p_names[i]
    is_hosted = p_config[first_p_name].can_host
    i += 1

    if i >= len(p_names):
      return None, False

    possible_coguest_len = 0
    if not is_hosted:
      group_gender = p_config[first_p_name].gender_if_single
      while (
        i + possible_coguest_len < len(p_names)
        and not (
          p_config[p_names[i+possible_coguest_len]].is_family
          or p_config[p_names[i+possible_coguest_len]].gender_if_single != group_gender
        )
      ):
        possible_coguest_len += 1
      if possible_coguest_len < _MIN_SINGLES_GROUP_SIZE:
        return None, False
      n_guests = random.randint(_MIN_SINGLES_GROUP_SIZE, min(possible_coguest_len, _MAX_SINGLES_GROUP_SIZE))
    if is_hosted:
      # p_names[i] is now the first guest participant. Figure out how many
      # co-guests are possible.
      # Constraint: at most one family, no large families with singles..
      possible_coguest_len = 0
      has_family = False
      has_singles = False
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
      n_guests = random.randint(1, min(possible_coguest_len, _MAX_GUEST_COUNT))
    member_names = p_names[i:i+n_guests] + [first_p_name]
    i += n_guests

    match = match_set.match.add()
    if is_hosted:
      match.host = first_p_name
    match.member.extend(sorted(member_names))
  return match_set, True
