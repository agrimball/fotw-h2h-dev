import copy
import datetime
import unittest

from src.org.fotw.h2h import h2h
from src.org.fotw.h2h import historian


class TestH2H(unittest.TestCase):

  def _make_simple_participant(self, name, can_host=True):
    return h2h.Participant(
      name=name,
      is_family=True,
      residence=name,
      participating=True,
      can_host=can_host,
      must_host_with="")

  def test_get_rel_dev_score(self):
    host_info = {
      "a": {
        "b": [datetime.datetime(2018, 10, 30)],
        "c": [datetime.datetime(2018, 10, 14), datetime.datetime(2018, 10, 1)],
      },
      "b": {"a": [datetime.datetime(2018, 10, 23), datetime.datetime(2018, 10, 1)]},
    }
    host_h = historian.from_dict(host_info)

    self.assertEqual(9, h2h.get_rel_dev_score("a", "b", host_h))
    self.assertEqual(4, h2h.get_rel_dev_score("a", "c", host_h))
    self.assertEqual(0, h2h.get_rel_dev_score("a", "d", host_h))

  def test_get_food_service_score(self):
    a = self._make_simple_participant("a")
    b = self._make_simple_participant("b")
    c = self._make_simple_participant("c", can_host=False)

    p_info = {a.name: a, b.name: b, c.name: c}

    food_h = historian.Historian()
    food_h.push_event_date('a', 'b', datetime.datetime(2018, 10, 30))
    food_h.push_event_date('a', 'c', datetime.datetime(2018, 10, 16))
    food_h.push_event_date('b', 'a', datetime.datetime(2018, 10, 16))
    food_h.push_event_date('b', 'a', datetime.datetime(2018, 10, 23))

    self.assertEqual(
        -2,  # 0 - 0 - 2
        h2h.get_food_service_score("a", p_info, food_h, datetime.datetime(2018, 10, 30)))
    self.assertEqual(
        -9,  # 0 - 7 - 2
        h2h.get_food_service_score("b", p_info, food_h, datetime.datetime(2018, 10, 30)))
    self.assertEqual(
        0,
        h2h.get_food_service_score("c", p_info, food_h, datetime.datetime(2018, 10, 30)))

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
        historian.from_dict(info_a),
        historian.from_dict(info_a),
        match_date)

    info_b = {
      a.name: {b.name: [datetime.datetime(2018, 10, 22)]},
      b.name: {a.name: [datetime.datetime(2018, 10, 30), datetime.datetime(2018, 10, 23)]},
    }
    score_b = h2h.get_match_config_score(
        p_info,
        historian.from_dict(info_b),
        historian.from_dict(info_b),
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
        historian.from_dict(info_a),
        historian.from_dict(info_a),
        match_date)

    info_b = {
      a.name: {
        b.name: [dt_a],
        d.name: [dt_a, dt_b, dt_b],
      },
      c.name: {
        b.name: [dt_a, dt_b, dt_b],
        d.name: [dt_a],
      },
    }
    score_b = h2h.get_match_config_score(
        p_info,
        historian.from_dict(info_b),
        historian.from_dict(info_b),
        match_date)

    # info_a is obviously a better configuration, so it should
    # have a higher score.
    self.assertTrue(score_a > score_b)

  def test_get_best_match_config(self):
    a = h2h.Participant(
      name="a",
      is_family=True,
      residence="2 Snow Ter",
      participating=True,
      can_host=True,
      must_host_with="")
    b = h2h.Participant(
      name="b",
      is_family=True,
      residence="4 Snow Ter",
      participating=True,
      can_host=True,
      must_host_with="")
    p_info = {a.name: a, b.name: b}

    host_historian = historian.Historian()
    host_historian.push_event_date(
        a.name, b.name, datetime.datetime(2018, 10, 22))
    host_historian.push_event_date(
        b.name, a.name, datetime.datetime(2018, 10, 23))
    food_historian = copy.deepcopy(host_historian)

    best_config = h2h.get_best_match_config(
      p_info,
      host_historian,
      food_historian,
      datetime.datetime(2018, 10, 30),
      10)
    expected_config = [
      h2h.Match(hosts=[a.name], cooks=[a.name], guests=[b.name])
    ]
    self.assertEqual(expected_config, best_config)


if __name__ == '__main__':
  unittest.main()
