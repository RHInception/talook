
from . import TestCase
from server import IndexHandler


class TestIndexHandler(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        self.instance = IndexHandler()

    def test_call(self):
        """
        Verify running IndexHandler returns proper information.
        """
        environ = {}
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        result = self.instance.__call__(environ, start_response)
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "text/html")]
        assert type(result) == str
