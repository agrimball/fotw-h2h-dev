from src.org.fotw.h2h.h2h_pb2 import MatchSet, Match

import random


_MAX_GUEST_COUNT = 2


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
    host_name = p_names[i]
    i += 1

    # Check that we're respecting the and can_host bits.
    if not p_config[host_name].can_host:
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
    n_guests = random.randint(1, min(possible_coguest_len, _MAX_GUEST_COUNT))
    guest_names = p_names[i:i+n_guests]
    i += n_guests

    match = match_set.match.add()
    match.host = host_name
    match.member.extend(sorted([host_name] + guest_names))
  return match_set, True