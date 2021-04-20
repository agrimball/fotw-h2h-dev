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

    n_guests = -1
    if not is_hosted:
      possible_coguest_len = 0
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


def gen_sprinkler_match_config(match_date, p_config):
  """
  Returns (matches, found_match) for a given participant config trying to
  match families with families and sprinkle singles in (and also trying
  not to overload families with 3+ additional singles).

  match_date is assumed to be a datetime.datetime object
  """
  p_names = [p_name for p_name in p_config if p_config[p_name].participating]
  host_names = [p_name for p_name in p_names if p_config[p_name].can_host]
  sprinkler_names = [p_name for p_name in p_names if not p_config[p_name].can_host]

  random.shuffle(host_names)
  random.shuffle(sprinkler_names)
  match_set = MatchSet(date_yyyymmdd=match_date.strftime('%Y%m%d'))

  # Get to an even number of host_names for matching below.
  if len(host_names) % 2 == 1:
    if not sprinkler_names:
      host_names.pop()  # That host just won't get to participate :(
    else:
      match = match_set.match.add()
      match.host = host_names.pop()
      match.member.extend(sorted([match.host, sprinkler_names.pop()]))

  if len(host_names) % 2 == 1:
    raise Exception('Impossible: host_names is not an even length!')

  # Make hostless singles groups so that families don't get overwhelmed
  # with 3+ singles on top of another family being hosted.
  while len(sprinkler_names) > len(host_names):
    # Make singles hostless groups
    m_singles = [x for x in sprinkler_names if p_config[x].gender_if_single == 'M']
    f_singles = [x for x in sprinkler_names if p_config[x].gender_if_single == 'F']
    other_sprinklers = [x for x in sprinkler_names if x not in m_singles and x not in f_singles]

    hostless_src = m_singles if len(m_singles) > len(f_singles) else f_singles
    if len(hostless_src) < _MIN_SINGLES_GROUP_SIZE:
      break # Allow overflow rather than drop singles

    n_singles = random.randint(_MIN_SINGLES_GROUP_SIZE, min(len(hostless_src), _MAX_SINGLES_GROUP_SIZE))
    gathering_members = []
    for i in range(n_singles):
      gathering_members.append(hostless_src.pop())
    
    match = match_set.match.add()
    match.member.extend(sorted(gathering_members))

    # Reconstructing it this way works because when popping from hostless_src,
    # we're also popping from the actual source list (m_singles or f_singles)
    # so sprinkler_names should shrink.
    sprinkler_names = other_sprinklers + m_singles + f_singles
    random.shuffle(sprinkler_names)

  # Match all the families together (since len(host_names) is even).
  for i in range(0, len(host_names), 2):
    match = match_set.match.add()
    match.host = host_names[i]
    match.member.extend(sorted([host_names[i], host_names[i+1]]))

  hosted_matches = [match for match in match_set.match if match.host]
  if hosted_matches:
    i = 0
    while sprinkler_names:
      hosted_matches[i].member.append(sprinkler_names.pop())
      i = (i + 1) % len(hosted_matches)

  return match_set, True
