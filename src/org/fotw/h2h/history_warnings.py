"""Detects bad signs in a given h2h hosting history."""

def get_warnings(host_history):
  warnings = []
  warnings += _get_repair_warnings(host_history)
  warnings += _get_hosting_fairness_warnings(host_history)
  return warnings


def _get_repair_warnings(host_history):
  warnings = []
  all_dates = set()
  for a in host_history.get_past_host_names():
    for b in host_history.get_past_guests(a):
      for event_date in host_history.get_host_dates(a, b):
        all_dates.add(event_date)

  sorted_dates = sorted(all_dates)
  last_3_dates = sorted_dates[len(sorted_dates)-3:]
  for a in host_history.get_all_names():
    for b in host_history.get_all_names():
      if b <= a:
        continue

      all_match_dates = host_history.get_meetup_dates(a, b)

      if last_3_dates[len(last_3_dates) - 1] not in all_match_dates:
        # if the most recent match doesn't contribute, then it doesn't matter.
        continue

      if last_3_dates[1] in all_match_dates and last_3_dates[2] in all_match_dates:
        warnings.append('SEVERE repair warning: %s & %s' % (a, b))
        continue

      repair_count = 0
      for x in last_3_dates:
        if x in all_match_dates:
          repair_count += 1
      if repair_count >= 2:
        warnings.append('MODERATE repair warning: %s & %s' % (a, b))
  return warnings


def _get_hosting_fairness_warnings(host_history):
  warnings = []
  all_dates = set()
  for a in host_history.get_past_host_names():
    for b in host_history.get_past_guests(a):
      for event_date in host_history.get_host_dates(a, b):
        all_dates.add(event_date)

  sorted_dates = sorted(all_dates)
  last_2_dates = sorted_dates[len(sorted_dates)-2:]
  for a in host_history.get_all_names():
    all_host_dates = []
    for b in host_history.get_all_names():
      all_host_dates += host_history.get_host_dates(a, b)
    all_host_dates = set(all_host_dates)

    if last_2_dates[0] in all_host_dates and last_2_dates[1] in all_host_dates:
      warnings.append('hosting fairness warning: %s hosted 2+ times' % a)
  return warnings
