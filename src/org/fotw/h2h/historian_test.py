from src.org.fotw.h2h import historian
from src.org.fotw.h2h.h2h_pb2 import MatchingHistory

from com_google_protobuf_python_srcs.python.google.protobuf import text_format

import datetime
import os
import unittest

class TestHistorian(unittest.TestCase):

  def test_zero_state(self):
    h = historian.Historian()

    # 0-state functions correctly.
    self.assertEqual([], h.get_host_dates('a', 'b'))
    self.assertEqual(set(), set(h.get_past_guests('a')))

  def test_push_pop_get(self):
    h = historian.Historian()

    event_date = datetime.datetime(2018, 10, 30)
    h.push_host_date('a', 'b', event_date)

    self.assertEqual([event_date], h.get_host_dates('a', 'b'))
    self.assertEqual(set(['b']), set(h.get_past_guests('a')))

    h.pop_host_date('a', 'b', event_date)
    self.assertEqual([], h.get_host_dates('a', 'b'))

  def test_pops_last_event_date(self):
    h = historian.Historian()

    event_date_a = datetime.datetime(2018, 10, 30)
    event_date_b = datetime.datetime(2018, 10, 31)

    h.push_host_date('a', 'b', event_date_a)
    h.push_host_date('a', 'b', event_date_b)

    self.assertEqual([event_date_a, event_date_b], h.get_host_dates('a', 'b'))

    h.pop_host_date('a', 'b', event_date_b)

    self.assertEqual([event_date_a], h.get_host_dates('a', 'b'))

  def test_date_ordering(self):
    h = historian.Historian()

    event_date_a = datetime.datetime(2018, 10, 30)
    event_date_b = datetime.datetime(2018, 10, 31)
    event_date_c = datetime.datetime(2018, 11, 1)

    # insert later date first.
    h.push_host_date('a', 'b', event_date_b)
    h.push_host_date('a', 'b', event_date_c)
    h.push_host_date('a', 'b', event_date_a)

    # dates are ordered independently of insert order.
    self.assertEqual(
        [event_date_a, event_date_b, event_date_c],
        h.get_host_dates('a', 'b'))

    h.pop_host_date('a', 'b', event_date_c)

    # pops last date.
    self.assertEqual([event_date_a, event_date_b], h.get_host_dates('a', 'b'))

  def test_write_textproto_str(self):
    test_srcdir = os.environ['TEST_SRCDIR']
    testing_textproto_path = test_srcdir + '/__main__/src/org/fotw/h2h/h2h-testing-textproto.txt'
    with open(testing_textproto_path, 'r') as testing_textproto:
      expected_textproto_str = testing_textproto.read()

    matching_history = MatchingHistory()
    text_format.Parse(expected_textproto_str, matching_history)
    h = historian.from_proto(matching_history)
    self.assertEqual(expected_textproto_str, text_format.MessageToString(h.to_proto()))


if __name__ == '__main__':
  unittest.main()
