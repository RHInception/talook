
import datetime
import json
import os
import socket
import tempfile

from . import TestCase
from server import BaseHandler


class TestBaseHandler(TestCase):

    def setUp(self):
        """
        Create an instance each time for testing.
        """
        os.environ['TALOOK_CONFIG_FILE'] = 'test/config.json'
        self.instance = BaseHandler()

    def test_config_loading(self):
        """
        Verify configuration loading.
        """
        assert type(self.instance._conf) == dict
        for key in ['hosts', 'endpoint', 'templatedir',
                    'cachedir', 'cachetime', 'logdir',
                    'staticdir', 'timeout']:
            assert key in self.instance._conf.keys()
        assert type(self.instance._conf['hosts']) == dict
        assert self.instance._conf['timeout'] == int(
            socket.getdefaulttimeout())
        #assert type(self.instance._conf['cachetime']) == dict

    def test_creation(self):
        """
        Test creation of BaseHandler.
        """
        assert self.instance._template_path
        assert type(self.instance._cache) == bool
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

    def test_save_to_cache(self):
        """
        Verify we are able to save cache via BaseHandler.save_to_cache()
        """
        self.instance._cache_dir = tempfile.gettempdir()
        assert self.instance.save_to_cache('test', '{"test": "data"}') is None

    def test_get_from_cache(self):
        """
        Verify BaseHandler.get_from_cache() returns proper data.
        """
        nodata = lambda: '["NOTHING"]'

        self.instance._cache_dir = tempfile.gettempdir()
        self.instance._cache = True
        data = {"test": "data"}
        json_data = json.dumps(data)
        assert self.instance.save_to_cache('test', json_data) is None
        assert json_data == self.instance.get_from_cache('test', nodata)
