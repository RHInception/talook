
try:
    import json
except ImportError:
    import simplejson as json

from . import TestCase
from server import QueryHostHandler


class TestQueryHostHandler(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        self.instance = QueryHostHandler()

    def test_call_with_invalid_input(self):
        """
        Verify running QueryHostHandler doesn't allow any host.
        """
        environ = {}
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        result = self.instance.__call__(
            environ, start_response, 'idonotexist.example.com')
        assert buffer['code'] == '404 File Not Found'
        assert buffer['headers'] == [("Content-Type", "text/html")]

    def test_call_with_valid_input(self):
        """
        Verify running QueryHostHandler returns expected results.
        """
        environ = {}
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        def get_from_cache_stub(key, source):
            return {"ok": {"result": "returned"}}

        self.instance.get_from_cache = get_from_cache_stub

        result = self.instance.__call__(
            environ, start_response, '127.0.0.1')
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "application/json")]
        data = json.loads(result)
        assert data == {"ok": {"result": "returned"}}
