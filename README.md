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
    
## Check that your server is behaving as expected (optional)

Using Python from a different process:

    import requests
    response = requests.get('http://localhost:8000/path1')
    print response.status_code               # expect 200
    print response.content                   # expect '{"foo": "bar"}'
    print response.headers['content-type']   # expect 'application/json'
    
Or using the Linux shell:

    $ curl "http://localhost:8000/path1/"
    
(expect {"foo": "bar"})

## Replace the third-party URL with the mock one

This will be done differently for each project.  Maybe you have an internal service which wraps the third-party service call where the URL of the third-party service can be set dynamically through the database or through the JSON/XML of the incoming request.

## Test your internal flow

Run your tests as usual.  Now the Chameleon mock server will be hit instead of the third-party system.  You will get back the hard-coded respinse content, status code, and content-type that you specified earlier.

## Clean up

Your automated test should end by shutting down the chameleon server:

    chameleon.stop()
    
After this, the following tests will be able to start their own chameleon servers to mock out different services or the same service in a different way.  There is no way to update the behavior of a running chameleon server, but it is inexpensive to bring up and shut down.
