from __future__ import print_function, unicode_literals

import itertools

import cherrypy
import six

try:
    import simplejson as json
except ImportError:
    import json  # noqa


def start(response_settings, port=8080):
    """
    Starts a minimal web server in the background which responds with the
    specified content, content-type and HTTP status code when the given URLs
    are POSTed to or GETed from.

    Useful for the purpose of mocking out expected third-party responses for
    automated testing.

    Args:
        response_settings (dict): a JSON-style list of dicts which contains all
            of the request and response params for the simulating server to use
            There should be one item in the list for each URL the service should
            listen to requests on.
            Each dictionary should contain a:
                * url: something like "/path1"
                * status_code: The HTTP status code to return.  E.g. 200
                * content_type: The mime-type of the response.
                                E.g. "text/xml" or "application/json"
                                     or "text/html"
                * content:  some JSON, XML, HTTP, or other string to return
                            as the response content.

            Example:
                [{"url": "/path1",
                  "status_code": 200,
                  "content_type": "application/json",
                  "content": "{'foo': 'bar'}"},
                 {"url": "/path2",
                  "status_code": 404,
                  "content_type": "text/html",
                  "content": "<html><body><p>Page not found</p></body></html>"},
                 {"url": "/path3",
                  "status_code": 200,
                  "content_type": "text/xml",
                  "content": "<foo>bar</foo>"},]

        port (int): the port number this server should run on.  Default is 8080.
            E.g. 9095
    """
    try:
        _validate_response_settings(response_settings)

        for setting in response_settings:
            url = setting['url']
            if not url.startswith('/'):
                url = '/' + url

            content = setting['content']
            content_type = setting['content_type']
            status_code = setting['status_code']

            config_instance = _get_cherrypy_page_handler(
                status_code, content_type, content
            )
            cherrypy.tree.mount(config_instance, url)

        cherrypy.config.update({'server.socket_port': port, })

        cherrypy.engine.start()

    except Exception as e:
        # TODO: Investigate; I think cherrypy kills the process before the
        # execution even reaches this point
        print("Exception '%s' occurred.  Killing the mock server." % str(e))
        stop()
        raise


def stop():
    """ Kills the server for the mock service.
    """
    cherrypy.engine.stop()
    cherrypy.server.httpserver = None


def _get_cherrypy_page_handler(status_code, content_type, content):
    class Foo(object):
        @cherrypy.expose
        @cherrypy.tools.json_out()
        def index(self, **kwargs):
            cherrypy.response.status = status_code
            cherrypy.response.headers['Content-Type'] = content_type
            return json.loads(content) if 'json' in content_type else content
    return Foo()


def _validate_response_settings(response_settings):
    """ Iterates through all the settings to check:
        - if they exist
        - if they are of the correct data type
    """
    error_message = "Please include a '{}' key for all response settings"
    required = ("url", "status_code", "content_type", "content",)

    # Not sure if this "type checking" will be scalable with multiple responses,
    # might be best to make it a configurable option and left to the user's
    # discretion. A 'strict' mode, if you please.
    for field, setting in itertools.product(required, response_settings):
        assert field in setting, error_message.format(field)
        assert isinstance(setting['url'], six.string_types)
        assert isinstance(setting['status_code'], six.integer_types)
        assert isinstance(setting['content_type'], six.string_types)
        assert isinstance(setting['content'], six.string_types)
