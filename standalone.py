#!/usr/bin/env python2

# TODO: Document and test me!!!


import urllib

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


def create_wsgi_wrapper(wsgi_app):
    """
    Wraps a WSGI application for use.
    """

    class WSGIWrapperHandler(BaseHTTPRequestHandler):

        def start_response(self, status, headers):
            # Handle status info
            # TODO: Handle network errors better.
            status_data = status.split(' ')
            if len(status_data) > 1:
                self.send_response(int(status_data[0]), status_data[1])
            else:
                self.send_response(int(status_data[0]))
            # Iterate over headers and send them out
            for name, value in headers:
                self.send_header(name, value)
            self.end_headers()

        def handle(self):
            self.environ = self.server._environ.copy()
            BaseHTTPRequestHandler.handle(self)

        def do_GET(self):
            if '?' in self.path:
                path, query = self.path.split('?', 1)
            else:
                path, query = (self.path, '')

            self.environ['QUERY_STRING'] = query
            self.environ['PATH_INFO'] = urllib.unquote(path)

            for chunk in wsgi_app(self.environ, self.start_response):
                self.wfile.write(chunk)

    return WSGIWrapperHandler


class WSGILiteServer(HTTPServer):
    """
    Not 100% WSGI compliant but enough for what we need.
    """

    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self._environ = {
            'SERVER_NAME': self.server_name,
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_PORT': str(self.server_port),
            'REMOTE_HOST': '',
        }


def main():
    # This is where you import your app
    from server import make_app
    app = make_app()
    server = WSGILiteServer(('0.0.0.0', 8000), create_wsgi_wrapper(app))
    server.serve_forever()


if __name__ == '__main__':
    main()
