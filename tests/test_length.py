#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pygpx import GPX


class RequestTest(unittest.TestCase):

    def test_length(self):
        gpx = GPX(open('tests/test_data/2012_06_30 21_17.gpx', 'r'))
        d = gpx.distance()
        d_calculated = 6000
        self.assertAlmostEqual(d, d_calculated, delta=100)


if __name__ == '__main__':
    unittest.main()
