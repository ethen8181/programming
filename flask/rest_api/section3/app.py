from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route('/')
def home():
    """
    Web 101
    -------
    Web server : a piece of software that's designed to accept incoming web requests.
    When we go to google.com (this is referred to as the host name) in our browser,
    we're sending a request to one of its web server.

    If we issue a GET request, the server might receive GET / HTTP/1.1,
    with "GET" being the verb, "/" being the url path and "HTTP/1.1" being the web protocol.
    After the server receives this request it will respond accordingly depending on the implementation.
    It may give you an error if the url path is not found, or if the server is down, or
    the expected result.

    Going to a web-page will always be a GET request, however, there're many other actions
    that we can do, e.g. POST, DELETE, PUT, and much more.
    Again, each server will respond differently to each action, but they normally entail
    similar meanings as per convention.

    Conventional actions:
    These are from the server's perspective, so from the browser's perspective it's actually flipped.

    POST : receive some input data and use it.
    PUT : similar to POST, but POST is mostly used for creating something, while PUT
    can also be used to update something.
    DELETE : remove something.

    REST
    ----
    One key feature of REST is that it is suppose to be stateless. This means
    that one request can't depend on any other request and all the information
    necessary to service the request is contained in the URL, query parameter. e.g.
    if we do POST /item/chair to create an item, the server does not know the item
    now exists, if we perform a GET /item/chair, the server needs to go to the database
    and check to see if the item is there.

    So if a user logs in to a web-application to access the REST, the web application must
    send enough data to identify the user in every request.

    Calling the API
    ---------------
    After creating the API, we can:
    1. Call it via javascript to show the result on a website. The python doesn't know
    what's going on over at the website, the same way javascript doesn't know anything
    about the python code. The two talks to each other via the API.

    """
    return 'Hello, world'


stores = [
    {
        'name': 'My Wonderful Store',
        'items': [
            {
                'name': 'My Item',
                'price': 15.99
            }
        ]
    }
]


@app.route('/store', methods=['POST'])
def create_store():
    # when testing the API using POSTMAN, we should add
    # the header's Content-Type to be application/json
    # and specify the json in the body.
    request_data = request.get_json()
    new_store = {
        'name': request_data['name'],
        'items': []
    }
    stores.append(new_store)
    return jsonify(new_store)


@app.route('/store/<string:name>')
def get_store(name):
    result = {'message': 'store not found'}
    for store in stores:
        if store['name'] == name:
            result = store
            break

    return jsonify(result)


@app.route('/store')
def get_stores():
    """Simply returns all the stores."""

    # json is required to be in a dictionary format, thus
    # we need to create a dictionary from the list of stores,
    # we can do this by just creating dictionary with 1 key.
    return jsonify({'stores': stores})


@app.route('/store/<string:name>/item', methods=['POST'])
def create_item_in_store(name):
    request_data = request.get_json()

    result = {'message': 'store not found'}
    for store in stores:
        if store['name'] == name:
            new_item = {
                'name': request_data['name'],
                'price': request_data['price']
            }
            store['items'].append(new_item)
            result = new_item
            break

    return jsonify(result)


@app.route('/store/<string:name>/item')
def get_items_in_store(name):
    result = {'message': 'store not found'}
    for store in stores:
        if store['name'] == name:
            result = {'items': store['items']}
            break

    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000)
