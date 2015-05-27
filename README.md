# Chameleon
Chameleon is a test server which can be used with the Python test frameworks like Robot Framework.
It mocks the behavior of third-party communications so that third party services do not need to be directly accessed during tests.  The goal is to remove outside dependencies from automated tests.

Here is an example scenario of how you would use this tool:

## Identify a scenrio where Chameleon would be useful

* Your communication to the third-party system uses HTTP requests
* Your communication to the third-party system is synchronous - you expect a direct response to your call.
* Your internal service which calls the third-party system takes the URI to call dynamically (i.e. the location of the third-party URI to call is not hard-coded)

## Spin up a Chameleon server as a replacement
Using your test framework, spin up a chameleon server to take the place of the real server that you want to mock out.

Example code:

    import chameleon
    settings_list = [{"url": "/path1", 
                      "status_code": 200, 
                      "content_type": "application/json", 
                      "content": '{"foo": "bar"}'},
                     {"url": "path2", 
                      "status_code": 404, 
                      "content_type": "text/html", 
                      "content": 'Page not found'}]
    chameleon.start(settings_list, port=8000)
    
