#!/usr/bin/env python
"""
Self contained stats consumer.
"""

import datetime
import os
import re
import threading
import time

try:
    import json
except ImportError:
    # Fallback for 2.4 and 2.5
    import simplejson as json

import urllib

import logging
import logging.handlers


def create_logger(name, filename,
                  format='%(asctime)s - %(levelname)s - %(message)s'):
    """
    Creates a logger instance.
    """
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        logger.setLevel(logging.INFO)
        logfile = os.path.sep.join([os.path.realpath(
            json.load(open(os.environ['TALOOK_CONFIG_FILE'], 'r'))['logdir']),
            filename])

        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        handler = logging.handlers.TimedRotatingFileHandler(
            logfile, 'd')
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(format))
        logger.addHandler(handler)
    return logger


class Router(object):
    """
    URL Router.
    """

    def __init__(self, rules):
        """
        Creates an application URI router.

        rules is a dictionary defining uri: WSGIApplication
        """
        self._rules = {}
        self.logger = create_logger('talook', 'talook_app.log')
        for uri, app in rules.items():
            self._rules[uri] = {'app': app, 'regex': re.compile(uri)}

    def reload(self):
        """
        Reruns init for all mounted WSGI apps.
        """
        self.logger.info('Reloading config')
        for key, value in self._rules.items():
            value['app'].__init__()

    def __call__(self, environ, start_response):
        """
        Callable which handles the actual routing in a WSGI structured way.
        """
        # If the path exists then pass control to the wsgi application
        if environ['PATH_INFO'] in self._rules.keys():
            return self._rules[environ['PATH_INFO']]['app'].__call__(
                environ, start_response)

        # If the path matches the regex then pass control to the wsgi app
        for uri, data in self._rules.items():
            # skip '' because it would always match
            if uri == '':
                continue
            if data['regex'].match(environ['PATH_INFO']):
                kwargs = data['regex'].match(environ['PATH_INFO']).groupdict()
                return data['app'].__call__(environ, start_response, **kwargs)

        # Otherwise 404
        start_response("404 File Not Found", [("Content-Type", "text/html")])
        return "404 File Not Found."


class BaseHandler(object):
    """
    Base handler to be used for app endpoints.
    """

    def __init__(self):
        """
        Creates a BaseHandler instance.
        """
        self._conf = json.load(open(os.environ['TALOOK_CONFIG_FILE'], 'r'))
        self.logger = create_logger('talook', 'talook_app.log')

        self._template_path = os.path.sep.join([os.path.realpath(
            self._conf['templatedir']), 'templates'])
        try:
            self._cache_dir = os.path.realpath(self._conf['cachedir'])
            self._cache_time = datetime.timedelta(**self._conf['cachetime'])
            self._cache = True
            self.logger.info(
                'Caching in %s is enabled' % self.__class__.__name__)
        except KeyError:
            self._cache = False
            self.logger.info(
                'Caching in %s is disabled' % self.__class__.__name__)

    def render_template(self, name, **kwargs):
        """
        Template renderer.
        """
        tpl = open(os.path.sep.join([self._template_path, name]), 'r').read()
        for key, value in kwargs.items():
            tpl = tpl.replace("{{- " + key + " -}}", value)
        return tpl

    def get_from_cache(self, key, source=None):
        """
        Gets data from a local cache. If it's not there it will run the
        source callable, save the result and return the results.
        """
        cache_name = os.path.sep.join([self._cache_dir, key + '.json'])
        if self._cache and os.path.exists(cache_name):
            mtime = datetime.datetime.fromtimestamp(
                os.stat(cache_name).st_mtime)
            now = datetime.datetime.now()
            # If we are still in the cache time then use the cache
            if now - self._cache_time < mtime:
                self.logger.info('Found "%s" in cache.' % key)
                data = open(cache_name, 'r').read()
                return data
            else:
                self.logger.info('Key "%s" is expired in cache.' % key)
        else:
            self.logger.info('Key "%s" was NOT in cache.' % key)

        try:
            data = source()
            if self._cache:
                self.save_to_cache(key, data)
            return data
        except Exception, ex:
            print ex

    def save_to_cache(self, key, data):
        """
        Holds data in local 'cache'.
        """
        cache_name = os.path.sep.join([self._cache_dir, key + '.json'])
        json_data = json.loads(data)
        f = open(cache_name, 'w')
        f.write(json.dumps(json_data))
        f.close()
        self.logger.info('Saved "%s" in cache.' % key)

    def return_404(self, start_response, msg="404 File Not Found"):
        """
        Shortcut for returning 404's.
        """
        start_response("404 File Not Found", [("Content-Type", "text/html")])
        return str(msg)


class StaticFileHandler(BaseHandler):
    """
    Handles static file serving. Will ONLY serve 1 directory deep!!
    """

    def __call__(self, environ, start_response, filename):
        """
        Returns the content of a CSS, JS or PNG file with the right mimetype
        if it exists.
        """
        real_name = os.path.sep.join(
            [os.path.realpath(self._conf['staticdir']), filename])
        if os.path.exists(real_name) and os.path.isfile(real_name):
            mime_type = 'text/plain'
            if real_name.endswith('.js'):
                mime_type = 'application/javascript'
            elif real_name.endswith('.css'):
                mime_type = 'text/css'
            elif real_name.endswith('.png'):
                mime_type = 'image/png'
            start_response("200 OK", [(
                "Content-Type", mime_type)])
            f = open(real_name, 'r')
            for line in f.readlines():
                yield line
            f.close()
        else:
            yield self.return_404(start_response)


class IndexHandler(BaseHandler):
    """
    Index page.
    """

    def __call__(self, environ, start_response):
        """
        Handles the index page.
        """
        start_response("200 OK", [("Content-Type", "text/html")])
        return self.render_template('base.html', title='Talook')


class ListHostsHandler(BaseHandler):
    """
    Hosts page.
    """

    def __call__(self, environ, start_response):
        """
        Handles the REST API endpoint listing known hosts.
        """
        start_response("200 OK", [("Content-Type", "application/json")])
        return json.dumps(self._conf['hosts'])


class ListEnvsHandler(BaseHandler):
    """
    Envs page.
    """

    def __call__(self, environ, start_response):
        """
        Handles the REST API endpoint listing known environments.
        """
        start_response("200 OK", [("Content-Type", "application/json")])
        return json.dumps(self._conf['hosts'].values())


class QueryHostHandler(BaseHandler):
    """
    talook page.
    """

    def __call__(self, environ, start_response, host):
        """
        Handles the REST API proxy between restfulstatsjson and the web ui.
        """
        if host in self._conf['hosts']:
            endpoint = self._conf['endpoint'] % host
            self.logger.info('Requesting data from %s' % endpoint)
            call_obj = lambda: str(urllib.urlopen(endpoint).read())

            data = self.get_from_cache(host, call_obj)
            json_data = json.loads(data)

            start_response("200 OK", [("Content-Type", "application/json")])
            return json.dumps(json_data)

        return self.return_404(start_response)


def create_server(host, port):
    """
    If the server is called directly then serve via wsgiref.
    """
    from wsgiref.simple_server import make_server, WSGIRequestHandler

    logger = create_logger(
        'talook_access', 'talook_access.log', '%(message)s')

    class TalookHandler(WSGIRequestHandler):

        def log_message(self, format, *args):
            logger.info("%s - - [%s] %s" % (
                self.address_string(),
                self.log_date_time_string(),
                format % args))

    app = make_app()

    return (make_server(
        host, int(port), app,
        handler_class=TalookHandler), app)


def create_old_server(host, port):
    """
    Code for running the old server.
    """

    import urllib
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

    def create_wsgi_wrapper(wsgi_app):
        """
        Wraps a WSGI application for use.
        """

        logger = create_logger(
            'talook_access', 'talook_access.log', '%(message)s')

        class WSGIWrapperHandler(BaseHTTPRequestHandler):

            def start_response(self, status, headers):
                """
                A fake WSGI start_response method.
                """
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

            # FIXME: This is being shared in another handler. Mixin?
            def log_message(self, format, *args):
                logger.info("%s - - [%s] %s" % (
                    self.address_string(),
                    self.log_date_time_string(),
                    format % args))

            def handle(self):
                """
                Overrides handle so that the environ is set.
                """
                self.environ = self.server._environ.copy()
                BaseHTTPRequestHandler.handle(self)

            def do_GET(self):
                """
                Since we only do GET we only need to define do_GET.
                """
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
            """
            Creates an instance of a fake WSGI server.
            """
            HTTPServer.__init__(self, *args, **kwargs)
            self._environ = {
                'SERVER_NAME': self.server_name,
                'GATEWAY_INTERFACE': 'CGI/1.1',
                'SERVER_PORT': str(self.server_port),
                'REMOTE_HOST': '',
            }

    app = make_app()
    return (WSGILiteServer((host, int(port)), create_wsgi_wrapper(app)), app)


class ServerThread(threading.Thread):
    """
    Thread for the server to run in.
    """

    def __init__(self, *args, **kwargs):
        """
        Creates the thread object and a logger.
        """
        threading.Thread.__init__(self, *args, **kwargs)
        self.logger = create_logger('talook', 'talook_app.log')

    def terminate(self):
        """
        How to signal the thread to end.
        """
        self.logger.debug(
            'ServerThread %s has been asked to terminate.' % self.getName())
        self.server.shutdown()

    def start(self, server):
        """
        How to start the thread.
        """
        self.server = server
        threading.Thread.start(self)

    def run(self):
        """
        How to run.
        """
        self.server.serve_forever()
        self.logger.info('ServerThread %s is exiting NOW!' % self.getName())
        raise SystemExit(0)


class ConfigPoller(ServerThread):
    """
    Thread for the config file poller to run in.
    """

    #: Variable to note if the poller should terminate
    _terminate = False

    def start(self, app):
        self.app = app
        self.logger = create_logger('talook', 'talook_app.log')
        threading.Thread.start(self)

    def terminate(self):
        """
        How to signal the thread to end.
        """
        self._terminate = True

    def run(self):
        """
        How to run.
        """
        mtime = os.stat(os.environ['TALOOK_CONFIG_FILE']).st_mtime
        while not self._terminate:
            current_mtime = os.stat(os.environ['TALOOK_CONFIG_FILE']).st_mtime
            if mtime != current_mtime:
                mtime = current_mtime
                try:
                    self.app.reload()
                    self.logger.info('Config has successfully reloaded.')
                except ValueError:
                    self.logger.error(
                        'JSON is invalid. Config was not reloaded.')
            time.sleep(1)
        raise SystemExit(0)


def make_app():
    """
    Creates a WSGI application for use.
    """
    return Router({
        '^/$': IndexHandler(),
        '/hosts.json$': ListHostsHandler(),
        '/envs.json$': ListEnvsHandler(),
        '/host/(?P<host>[\w\.\-]*).json?$': QueryHostHandler(),
        '/static/(?P<filename>[\w\-\.]*$)': StaticFileHandler(),
    })


def main():
    import platform
    # Using optparse since argparse is not available in 2.5
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-c', '--config', dest='config', default='config.json',
                      help='Config file to read (Default: config.json')
    parser.add_option('-p', '--port', dest='port', default=8080, type='int',
                      help='Port to listen on. (Default: 8080)')
    parser.add_option(
        '-l', '--listen', dest='listen', default='0.0.0.0',
        help='Address to listen on. (Default: 0.0.0.0)')
    parser.add_option(
        '-r', '--reload', dest='reload', default=False, action='store_true',
        help='Enable reloading on config change. (Default: False)')

    (options, args) = parser.parse_args()

    os.environ['TALOOK_CONFIG_FILE'] = options.config
    py_version = platform.python_version()

    server = None
    # Fall back to old school container if on 2.4.x
    if py_version >= '2.4.0' and py_version < '2.5.0':
        server, app = create_old_server(options.listen, options.port)
    # Else use the builtin wsgi container
    elif py_version >= '2.5.0':
        server, app = create_server(options.listen, options.port)
    else:
        print 'Untested Python version in use: %s' % py_version
        raise SystemExit(1)

    if options.reload:
        config_poller_thread = ConfigPoller()
        config_poller_thread.setDaemon(True)
        config_poller_thread.start(app)

    print "server listening on http://%s:%s" % (options.listen, options.port)
    server_thread = ServerThread()
    server_thread.setDaemon(True)
    server_thread.start(server)

    # Main loop (even though all real work is in threads)
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            if options.reload:
                config_poller_thread.terminate()
                config_poller_thread.join()
            server_thread.terminate()
            server_thread.join()
            raise SystemExit(0)

    raise SystemExit(0)


if __name__ == "__main__":
    main()
