
import datetime

from . import TestCase
from server import BaseHandler


class TestBaseHandler(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        self.instance = BaseHandler()

    def test_config_loading(self):
        """
        Verify configuration loading.
        """
        assert type(self.instance._conf) == dict
        for key in ['hosts', 'endpoint', 'templatedir',
                    'cachedir', 'cachetime', 'logdir', 'staticdir']:
            assert key in self.instance._conf.keys()
        assert type(self.instance._conf['hosts']) == dict
        assert type(self.instance._conf['cachetime']) == dict

    def test_creation(self):
        """
        Test creation of BaseHandler.
        """
        assert self.instance._template_path
        assert self.instance._cache_dir
        assert type(self.instance._cache_time) == datetime.timedelta

    def test_render_template(self):
        """
        Verify template rendering works as expected.
        """
        rendered = self.instance.render_template('base.html', title='test')
        assert type(rendered) == str
        assert '<title>test</title>' in rendered

    def test_return_404(self):
        """
        Test 404 creation returns properly.
        """
        buffer = {}

        def start_response(code, headers):
            buffer['code'] = code
            buffer['headers'] = headers

        result = self.instance.return_404(
            start_response, msg="404 File Not Found")
        assert buffer['code'] == '404 File Not Found'
        assert buffer['headers'] == [('Content-Type', 'text/html')]
        assert result == '404 File Not Found'
