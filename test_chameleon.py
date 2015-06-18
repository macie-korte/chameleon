import unittest
import chameleon
import requests


class ChameleonTests(unittest.TestCase):
    def setUp(self):
        self.port = 7001  # uncommon port

    def tearDown(self):
        chameleon.stop()

    def test_basic_json_service(self):
        """
        Mock server with a single URL returning a successful JSON response
        responds to queries as expected.
        """
        settings_list = [{
            "url": "/path1",
            "status_code": 200,
            "content_type": "application/json",
            "content": '{"foo": "bar"}'
        }]

        chameleon.start(settings_list, port=self.port)
        response = requests.get('http://localhost:{}/path1'.format(self.port))

        # basic content stuff
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"foo": "bar"}')

        # ensure response decoded as JSON.
        self.assertEqual(response.json()['foo'], 'bar')
        self.assertEqual(response.headers['content-type'], 'application/json')

    def test_content_type_xml(self):
        settings_list = [{
            "url": "/path1",
            "status_code": 200,
            "content_type": "application/xml",
            "content": '<foo>bar</foo>'
        }]
        chameleon.start(settings_list, port=self.port)
        response = requests.get('http://localhost:{}/path1'.format(self.port))
        self.assertEqual(response.content, b'"<foo>bar</foo>"')
        self.assertEqual(response.headers['content-type'], 'application/xml')

    def test_multiple_services(self):
        """
        Multiple URLs can be served by the mock server at once.
        Custom ports other than 8080 also work.
        """
        settings_list = [
            {"url": "/path1",
             "status_code": 200,
             "content_type": "application/json",
             "content": '{"foo": "bar"}'},
            {"url": "path2",
             "status_code": 404,
             "content_type": "text/html",
             "content": 'Page not found'}
        ]
        chameleon.start(settings_list, port=self.port)

        # test path1 - the successful response
        response = requests.get('http://localhost:{}/path1'.format(self.port))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"foo": "bar"}')
        self.assertEqual(response.json()['foo'], 'bar')  # ensure response decoded as JSON.
        self.assertEqual(response.headers['content-type'], 'application/json')

        # test path2 - the page-not-found path
        response = requests.get('http://localhost:{}/path2'.format(self.port))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'"Page not found"')
        self.assertTrue(
            response.headers['content-type'].startswith('text/html')
        )

    @unittest.expectedFailure
    def test_strict_mode(self):
        """Placeholder: Not implemented yet """
        self.assertFalse(True)


if __name__ == '__main__':
    unittest.main()
