import datetime
import unittest

from src.org.fotw.h2h import historian
from src.org.fotw.h2h import history_warnings

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
        len(history_warnings.get_warnings(historian.Historian())))
