
from . import TestCase
from server import StaticFileHandler


class TestStaticFileHandler(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        self.instance = StaticFileHandler()

    def test_call(self):
        """
        Verify running StaticHandler returns propert information.
        """
        environ = {'PATH_INFO': '/static/style.css'}
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        def combine_result(iter):
            result = []
            for line in iter:
                result.append(line)
            return "\n".join(result)

        result = combine_result(
            self.instance.__call__(environ, start_response, 'style.css'))
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [("Content-Type", "text/css")]
        assert type(result) == str

        result2 = combine_result(
            self.instance.__call__(
                environ, start_response, 'bootstrap.min.js'))
        assert buffer['code'] == '200 OK'
        assert buffer['headers'] == [(
            "Content-Type", "application/javascript")]
        assert type(result2) == str

        result_404 = combine_result(
            self.instance.__call__(
                environ, start_response, 'nothing_here'))
        assert buffer['code'] == '404 File Not Found'
        assert buffer['headers'] == [(
            "Content-Type", "text/html")]
        assert type(result_404) == str
