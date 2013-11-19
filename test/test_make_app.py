
from . import TestCase
from server import Router, make_app


class TestMakeApp(TestCase):

    def test_make_app(self):
        """
        Verify make_app() creates a valid Router instance.
        """
        result = make_app()
        assert type(result) == Router
        assert callable(result)
