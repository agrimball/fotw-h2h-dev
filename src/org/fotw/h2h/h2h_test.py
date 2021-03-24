import copy
import datetime
import unittest

from src.org.fotw.h2h import h2h
from src.org.fotw.h2h import historian
from src.org.fotw.h2h.h2h_pb2 import Match, MatchSet


def _dict_to_historian(d):
  host_h = historian.Historian()
  for a in d.keys():
    for b in d[a].keys():
      for event_date in d[a][b]:
        host_h.push_host_date(a, b, event_date)
  return host_h


class TestH2H(unittest.TestCase):

  def _make_simple_participant(self, name, can_host=True):
    return h2h.Participant(
      name=name,
      is_family=True,
      residence=name,
      participating=True,
      can_host=can_host,
      child_count=0,
      gender_if_single='')

  def test_get_rel_dev_score(self):
    host_info = {
      "a": {
        "b": [datetime.datetime(2018, 10, 30)],
        "c": [datetime.datetime(2018, 10, 14), datetime.datetime(2018, 10, 1)],
      },
      "b": {"a": [datetime.datetime(2018, 10, 23), datetime.datetime(2018, 10, 1)]},
    }
    
    host_h = _dict_to_historian(host_info)

    self.assertEqual(9, h2h.get_rel_dev_score("a", "b", host_h))
    self.assertEqual(4, h2h.get_rel_dev_score("a", "c", host_h))
    self.assertEqual(0, h2h.get_rel_dev_score("a", "d", host_h))

  def test_get_match_config_score_load_balances_hosting(self):
    a = self._make_simple_participant("a")
    b = self._make_simple_participant("b")
    p_info = {a.name: a, b.name: b}

    match_date = datetime.datetime(2018, 10, 30)
    info_a = {
      a.name: {b.name: [datetime.datetime(2018, 10, 30), datetime.datetime(2018, 10, 1)]},
      b.name: {a.name: [datetime.datetime(2018, 10, 23)]},
    }
    score_a = h2h.get_match_config_score(
        p_info,
        _dict_to_historian(info_a),
        match_date)

    info_b = {
      a.name: {b.name: [datetime.datetime(2018, 10, 22)]},
      b.name: {a.name: [datetime.datetime(2018, 10, 30), datetime.datetime(2018, 10, 23)]},
    }
    score_b = h2h.get_match_config_score(
        p_info,
        _dict_to_historian(info_b),
        match_date)

    # info_a is obviously a better configuration, so it should
    # have a higher score.
    self.assertTrue(score_a > score_b)

  def test_get_match_config_score_balances_rel_dev(self):
    a = self._make_simple_participant("a")
    b = self._make_simple_participant("b", can_host=False)
    c = self._make_simple_participant("c")
    d = self._make_simple_participant("d", can_host=False)
    p_info = {a.name: a, b.name: b, c.name: c, d.name: d}

    match_date = datetime.datetime(2018, 10, 30)
    dt_a = datetime.datetime(2018, 10, 22)
    dt_b = datetime.datetime(2018, 10, 21)
    dt_c = datetime.datetime(2018, 10, 20)
    info_a = {
      a.name: {
        b.name: [dt_a, dt_b],
        d.name: [dt_a, dt_b],
      },
      c.name: {
        b.name: [dt_a, dt_b],
        d.name: [dt_a, dt_b],
      },
    }
    score_a = h2h.get_match_config_score(
        p_info,
        _dict_to_historian(info_a),
        match_date)

    info_b = {
      a.name: {
        b.name: [dt_a],
        d.name: [dt_a, dt_b, dt_c],
      },
      c.name: {
        b.name: [dt_a, dt_b, dt_c],
        d.name: [dt_a],
      },
    }
    score_b = h2h.get_match_config_score(
        p_info,
        _dict_to_historian(info_b),
        match_date)

    # info_a should be a better configuration since the hosting badness should be identical
    # but the relationship development is more evenly spread.
    self.assertTrue(score_a > score_b)

  def test_get_best_match_config(self):
    a = h2h.Participant(
      name="a",
      is_family=True,
      residence="2 Snow Ter",
      participating=True,
      can_host=True,
      child_count=0,
      gender_if_single='')
    b = h2h.Participant(
      name="b",
      is_family=True,
      residence="4 Snow Ter",
      participating=True,
      can_host=True,
      child_count=0,
      gender_if_single='')
    p_info = {a.name: a, b.name: b}

    host_historian = historian.Historian()
    host_historian.push_host_date(
        a.name, b.name, datetime.datetime(2018, 10, 22))
    host_historian.push_host_date(
        b.name, a.name, datetime.datetime(2018, 10, 23))

    best_config, _ = h2h.get_best_match_config(
      p_info,
      host_historian,
      datetime.datetime(2018, 10, 30),
      10)
    expected_config = MatchSet(
      date_yyyymmdd="20181030",
      match=[Match(host=a.name, member=[a.name, b.name])],
    )
    
    self.assertEqual(expected_config, best_config)


if __name__ == '__main__':
  unittest.main()
