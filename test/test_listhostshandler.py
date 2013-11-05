
import json

from . import TestCase
from server import ListHostsHandler


class TestListHostsHandler(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        self.instance = ListHostsHandler()

    def test_call(self):
        """
        Verify running ListHostsHandler returns proper information.
        """
        environ = {}
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        result = self.instance.__call__(environ, start_response)
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "application/json")]
        assert type(result) == str

        results = json.loads(result)
        assert results == self.instance._conf['hosts']
