import cherrypy
import requests
import simplejson as json
from   types import StringType, IntType


def start(response_settings, port=8080):
    """
    Starts a minimal web server in the background which responds with the
    specified content, content-type and HTTP status code when the given URLs
    are POSTed to or GETed from.

    Useful for the purpose of mocking out expected third-party responses for
    automated testing.

    Args:
        response_settings (dict): a JSON-style list of dicts which contains all of the 
            request and response params for the simulating server to use
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
                [{"url": "/path1", "status_code": 200, "content_type": "application/json", 
                  "content": "{'foo': 'bar'}"},
                 {"url": "/path2", "status_code": 404, "content_type": "text/html", 
                  "content": "<html><body><p>Page not found!</p></body></html>"},
                 {"url": "/path3", "status_code": 200, "content_type": "text/xml", 
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

            config_instance = _get_cherrypy_page_handler(status_code, content_type, content)
            cherrypy.tree.mount(config_instance, url)

        cherrypy.config.update({'server.socket_port': port})
        cherrypy.engine.start()
    except Exception, e:
        print "Exception '%s' occurred.  Killing the mock server." % str(e)
        stop_mock_service()
        raise


def stop():
    """ Kills the server for the mock service.
    """
    cherrypy.engine.stop()


def _get_cherrypy_page_handler(status_code, content_type, content):
    class Foo(object):
        @cherrypy.expose
        def index(self, **kwargs):
            cherrypy.response.status = status_code
            cherrypy.response.headers['Content-Type']= content_type
            return content
    return Foo()


def _validate_response_settings(response_settings):
    for setting in response_settings:
        assert "url" in setting, "Please include a 'url' key for all response settings"
        assert "status_code" in setting, "Please include a 'status_code' key for all response settings"
        assert "content_type" in setting, "Please include a 'content_type' key for all response settings"
        assert "content" in setting, "Please include a 'content' key for all response settings"
        assert type(setting['url']) is StringType
        assert type(setting['status_code']) is IntType
        assert type(setting['content_type']) is StringType
        assert type(setting['content']) is StringType
