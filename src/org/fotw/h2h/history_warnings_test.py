import datetime
import unittest

from src.org.fotw.h2h import historian
from src.org.fotw.h2h import history_warnings


def _dict_to_historian(d):
  host_h = historian.Historian()
  for a in d.keys():
    for b in d[a].keys():
      for event_date in d[a][b]:
        host_h.push_host_date(a, b, event_date)
  return host_h


class TestHistoryWarnings(unittest.TestCase):

  def test_zero_state(self):
    self.assertEqual(
        [],
        history_warnings.get_warnings(historian.Historian()))

  def test_repair_warning(self):
    host_info = {
      "a": {
        "b": [datetime.datetime(2018, 10, 30)],
        "c": [datetime.datetime(2018, 10, 14)],
      },
      "b": {"a": [datetime.datetime(2018, 10, 23)]},
    }
    self.assertEqual(
        1,
        len(history_warnings.get_warnings(_dict_to_historian(host_info))))
