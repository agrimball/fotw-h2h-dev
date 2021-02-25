import datetime
import os
import unittest

from src.org.fotw.h2h import historian

class TestHistorian(unittest.TestCase):

  def test_zero_state(self):
    h = historian.Historian()

    # 0-state functions correctly.
    self.assertEqual([], h.get_event_dates('a', 'b'))
    self.assertEqual(set(), set(h.get_associates('a')))

  def test_push_pop_get(self):
    h = historian.Historian()

    event_date = datetime.datetime(2018, 10, 30)
    h.push_event_date('a', 'b', event_date)

    self.assertEqual([event_date], h.get_event_dates('a', 'b'))
    self.assertEqual(set(['b']), set(h.get_associates('a')))

    h.pop_event_date('a', 'b')
    self.assertEqual([], h.get_event_dates('a', 'b'))

  def test_pops_last_event_date(self):
    h = historian.Historian()

    event_date_a = datetime.datetime(2018, 10, 30)
    event_date_b = datetime.datetime(2018, 10, 31)

    h.push_event_date('a', 'b', event_date_a)
    h.push_event_date('a', 'b', event_date_b)

    self.assertEqual([event_date_a, event_date_b], h.get_event_dates('a', 'b'))

    h.pop_event_date('a', 'b')

    self.assertEqual([event_date_a], h.get_event_dates('a', 'b'))

  def test_date_ordering(self):
    h = historian.Historian()

    event_date_a = datetime.datetime(2018, 10, 30)
    event_date_b = datetime.datetime(2018, 10, 31)
    event_date_c = datetime.datetime(2018, 11, 1)

    # insert later date first.
    h.push_event_date('a', 'b', event_date_b)
    h.push_event_date('a', 'b', event_date_c)
    h.push_event_date('a', 'b', event_date_a)

    # dates are ordered independently of insert order.
    self.assertEqual(
        [event_date_a, event_date_b, event_date_c],
        h.get_event_dates('a', 'b'))

    h.pop_event_date('a', 'b')

    # pops last date.
    self.assertEqual([event_date_a, event_date_b], h.get_event_dates('a', 'b'))

  def test_parse_and_write_testing_csv(self):
    test_srcdir = os.environ['TEST_SRCDIR']
    testing_csv_path = test_srcdir + '/__main__/src/org/fotw/h2h/h2h-testing-csv.csv'
    with open(testing_csv_path, 'r') as testing_csv:
      testing_csv_str = testing_csv.read()

    h = historian.parse_from_csv_str(testing_csv_str)
    self.assertEqual([], h.get_event_dates('Christian', 'Earl'))
    self.assertEqual(
        [datetime.datetime(2018, 7, 11)],
        h.get_event_dates('Christian', 'Weavers'))
    self.assertEqual([], h.get_event_dates('Earl', 'Christian'))
    self.assertEqual([], h.get_event_dates('Earl', 'Weavers'))
    self.assertEqual([], h.get_event_dates('Weavers', 'Christian'))
    self.assertEqual(
        [datetime.datetime(2017, 11, 29), datetime.datetime(2018, 4, 25)],
        h.get_event_dates('Weavers', 'Earl'))
    self.assertEqual([], h.get_event_dates('Weavers', 'Weavers'))

  def test_roundtrip_csv(self):
    h = historian.Historian()

    event_date_a = datetime.datetime(2018, 10, 30)
    event_date_b = datetime.datetime(2018, 10, 31)
    event_date_c = datetime.datetime(2018, 11, 1)

    # insert later date first.
    h.push_event_date('a', 'b', event_date_b)
    h.push_event_date('a', 'b', event_date_c)
    h.push_event_date('b', 'a', event_date_a)
    h.push_event_date('c', 'a', event_date_a)

    h2 = historian.parse_from_csv_str(h.write_to_csv_str('Host'))

    self.assertEqual(h.get_all_names(), h2.get_all_names())
    for a in h.get_all_names():
      for b in h.get_all_names():
        self.assertEqual(h.get_event_dates(a, b), h2.get_event_dates(a, b))

  def test_roundtrip_dict(self):
    h = historian.Historian()

    event_date_a = datetime.datetime(2018, 10, 30)
    event_date_b = datetime.datetime(2018, 10, 31)
    event_date_c = datetime.datetime(2018, 11, 1)

    # insert later date first.
    h.push_event_date('a', 'b', event_date_b)
    h.push_event_date('a', 'b', event_date_c)
    h.push_event_date('b', 'a', event_date_a)
    h.push_event_date('c', 'a', event_date_a)

    h2 = historian.from_dict(h.to_dict())

    self.assertEqual(h.get_all_names(), h2.get_all_names())
    for a in h.get_all_names():
      for b in h.get_all_names():
        self.assertEqual(h.get_event_dates(a, b), h2.get_event_dates(a, b))


if __name__ == '__main__':
  unittest.main()
