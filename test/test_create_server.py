
import sys

from StringIO import StringIO

from . import TestCase

import server


# Mockings
def create_server_mock(host, port):
    assert type(host) == str
    assert type(port) == int
    raise SystemExit(0)

server.create_old_server = create_server_mock
server.create_server = create_server_mock


class TestCreateServerInput(TestCase):

    def test_create_server_input(self):
        """
        Verify the input when creating servers is always correct.
        """
        # This case should cast 8080 to an int
        sys.argv = ['server.py']
        sys.argv.append('-l 127.0.0.1')
        sys.argv.append('-p 8080')
        self.assertRaises(SystemExit, server.main)

        # This case can't cast tasty tacos to integers.
        # Make sure we get a parser error and invalid int warning
        sys.argv[1] = '-l 127.0.0.1'
        sys.argv[2] = '-p taco'
        out_buff = StringIO()
        sys.stderr = out_buff
        try:
            server.main()
        except SystemExit, ex:
            assert ex.message == 2
            out_buff.seek(0)
            assert 'invalid integer' in out_buff.read()
