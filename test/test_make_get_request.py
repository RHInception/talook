
from . import TestCase

from cStringIO import StringIO

from server import make_get_request, urllib2


# Sub for urllib2.urlopen
def stub_urlopen(endpoint):
    if endpoint == 'http://127.0.0.1/test.json':
        return StringIO('{"test": "response"}')
    elif endpoint == 'http://127.0.0.1/nonjson.txt':
        return StringIO('not json data')
    elif endpoint == 'http://127.0.0.1/noconnection.json':
        raise urllib2.URLError(reason='can not connect')
    raise urllib2.HTTPError(endpoint, 500, 'test', {}, StringIO())


urllib2.urlopen = stub_urlopen


class TestMakeGetRequest(TestCase):

    def test_make_get_request_works(self):
        """
        Verify make_get_request returns json if data is returned.
        """
        result = make_get_request('http://127.0.0.1/test.json')
        assert type(result) == tuple
        assert type(result[0]) == int
        assert type(result[1]) == dict

    def test_make_get_request_erros_on_non_json_response(self):
        """
        Verify make_get_request returns json if data is returned.
        """
        result = make_get_request('http://127.0.0.1/nonjson.txt')
        assert type(result) == tuple
        assert type(result[0]) == int
        assert result[0] == -1
        assert type(result[1]) == dict
        assert 'error' in result[1].keys()
        assert 'Error' in result[1]['error'].keys()

    def test_make_get_request_unable_to_connect(self):
        """
        Verify make_get_request gracefully handles not being able to connect.
        """
        result = make_get_request('http://127.0.0.1/noconnection.json')
        assert type(result) == tuple
        assert type(result[0]) == int
        # Unable to connect has a code of -1
        assert result[0] == -1
        assert type(result[1]) == dict
        # Verify the error response structure is correct
        assert 'error' in result[1].keys()
        for key in ['Error', 'Reason', 'Suggestion']:
            assert key in result[1]['error'].keys()

    def test_make_get_general_error(self):
        """
        Verify make_get_request gracefully handles other errors.
        """
        result = make_get_request('http://127.0.0.1/error.json')
        assert type(result) == tuple
        assert type(result[0]) == int
        assert type(result[1]) == dict
        # Verify the error response structure is correct
        assert 'error' in result[1].keys()
        for key in ['Error', 'Reason', 'Suggestion']:
            assert key in result[1]['error'].keys()
