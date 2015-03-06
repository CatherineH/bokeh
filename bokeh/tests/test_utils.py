from __future__ import absolute_import

import unittest
from unittest import skipIf

import logging
from mock import patch

from bokeh.util.platform import is_py3, is_pypy
from bokeh.util.serialization import get_json, json_apply, make_id, resolve_json, urljoin


def skipIfPy3(message):
    return skipIf(is_py3(), message)


def skipIfPyPy(message):
    return skipIf(is_pypy(), message)


class DummyRequestCallable():
    def json(self):
        return True


class DummyRequestProperty():
    json = True


class TestMakeId(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(len(make_id()), 36)
        self.assertTrue(isinstance(make_id(), str))

    def test_simple_ids(self):
        import os
        os.environ["BOKEH_SIMPLE_IDS"] = "yes"
        self.assertEqual(make_id(), "1001")
        self.assertEqual(make_id(), "1002")
        del os.environ["BOKEH_SIMPLE_IDS"]

class TestUrlJoin(unittest.TestCase):
    def test_urljoin(self):
        result1 = urljoin('http://www.bokeh.com', 'test/')
        self.assertEqual(result1, 'http://www.bokeh.com/test/')
        result2 = urljoin('http://www.bokeh.com', 'test1/', 'test2/',
                          'test3/', 'bokeh.html')
        self.assertEqual(result2, 'http://www.bokeh.com/test1/test2/test3/bokeh.html')
        result3 = urljoin('http://www.notbokeh.com', 'http://www.bokeh.com/',
                          'test1/', 'bokeh1.squig')
        self.assertEqual(result3, 'http://www.bokeh.com/test1/bokeh1.squig')


class TestGetJson(unittest.TestCase):
    def test_with_property(self):
        self.assertTrue(get_json(DummyRequestProperty()))

    def test_with_method(self):
        self.assertTrue(get_json(DummyRequestCallable()))

class TestJsonapply(unittest.TestCase):

    def test_jsonapply(self):

        def check_func(frag):
            if frag == 'goal':
                return True

        def func(frag):
            return frag + 'ed'

        result = json_apply('goal', check_func, func)
        self.assertEqual(result, 'goaled')
        result = json_apply([[['goal', 'junk'], 'junk', 'junk']], check_func, func)
        self.assertEqual(result, [[['goaled', 'junk'], 'junk', 'junk']])
        result = json_apply({'1': 'goal', 1.5: {'2': 'goal', '3': 'junk'}}, check_func, func)
        self.assertEqual(result, {'1': 'goaled', 1.5: {'2': 'goaled', '3': 'junk'}})


class TestResolveJson(unittest.TestCase):

    @patch('bokeh.util.serialization.log')
    def test_resolve_json(self, mock_log):

        models = {'foo': 'success', 'otherfoo': 'othersuccess'}
        fragment = [{'id': 'foo', 'type': 'atype'}, {'id': 'foo', 'type': 'atype'}, {'id': 'otherfoo', 'type': 'othertype'}]
        self.assertEqual(resolve_json(fragment, models), ['success', 'success', 'othersuccess'])
        fragment.append({'id': 'notfoo', 'type': 'badtype'})
        self.assertEqual(resolve_json(fragment, models), ['success', 'success', 'othersuccess', None])
        self.assertTrue(mock_log.error.called)
        self.assertTrue('badtype' in repr(mock_log.error.call_args))

if __name__ == "__main__":
    unittest.main()
