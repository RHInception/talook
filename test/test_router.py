
import re

from . import TestCase
from server import Router, IndexHandler


class TestRouter(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        self.instance = Router({
            '/': IndexHandler(),
            '': IndexHandler(),
            '/test/location[s]?$': IndexHandler(),
        })

    def test_creation(self):
        """
        Verify creation of the Router works as expected.
        """
        router = Router({})
        assert router._rules == {}
        assert len(self.instance._rules) == 3
        assert 'regex' in self.instance._rules['/'].keys()
        assert 'app' in self.instance._rules['/'].keys()
        assert callable(self.instance._rules['/']['app'])
        assert self.instance._rules['/']['regex'].findall('/')

    def test_call(self):
        """
        Verify the router routes properly on valid URLs.
        """
        environ = {'PATH_INFO': '/'}
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        result = self.instance.__call__(environ, start_response)
        assert type(result) == str
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "text/html")]

        environ = {'PATH_INFO': 'bad'}
        result_404 = self.instance.__call__(environ, start_response)
        assert buffer['code'] == '404 File Not Found'
        assert buffer['headers'] == [("Content-Type", "text/html")]
        assert type(result_404) == str

        # RegEx matching
        environ = {'PATH_INFO': '/test/location'}
        result_regex = self.instance.__call__(environ, start_response)
        assert type(result_regex) == str
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "text/html")]

        # Verify we skip regex checks on ''
        environ = {'PATH_INFO': ''}
        result_empty_str = self.instance.__call__(environ, start_response)
        assert type(result_empty_str) == str
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "text/html")]
