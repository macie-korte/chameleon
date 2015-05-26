import unittest
import chameleon
import requests
import simplejson as json

class ChameleonTests(unittest.TestCase):
    def tearDown(self):
        chameleon.stop()

    def test_basic_json_service(self):
        """
        Mock server with a single URL returning a successful JSON response
        responds to queries as expected.
        Port defaults to 8080.
        """
        settings_list = [{"url": "/path1", 
                          "status_code": 200, 
                          "content_type": "application/json", 
                          "content": '{"foo": "bar"}'}]
        chameleon.start(settings_list)
        response = requests.get('http://localhost:8080/path1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"foo": "bar"}')
        self.assertEqual(response.json()['foo'], 'bar')  # ensure response decoded as JSON.
        self.assertEqual(response.headers['content-type'], 'application/json')

    def test_multiple_services(self):
        """
        Multiple URLs can be served by the mock server at once.
        Custom ports other than 8080 also work.
        """
        settings_list = [{"url": "/path1", 
                          "status_code": 200, 
                          "content_type": "application/json", 
                          "content": '{"foo": "bar"}'},
                         {"url": "path2", 
                          "status_code": 404, 
                          "content_type": "text/html", 
                          "content": 'Page not found'}]
        chameleon.start(settings_list, port=8000)

        # test path1 - the successful response
        response = requests.get('http://localhost:8000/path1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"foo": "bar"}')
        self.assertEqual(response.json()['foo'], 'bar')  # ensure response decoded as JSON.
        self.assertEqual(response.headers['content-type'], 'application/json')

        # test path2 - the page-not-found path
        response = requests.get('http://localhost:8000/path2')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'Page not found')
        self.assertTrue(response.headers['content-type'].startswith('text/html'))