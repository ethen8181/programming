import sqlite3
from flask_jwt import jwt_required
from flask_restful import Resource, reqparse


class Item(Resource):
    """Many APIs are like this, CRUD, create, read, update, delete."""

    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True,
                        help='item price must be passed with the payload')

    # we no longer need jsonify as inheriting the Resource
    # class gives us that for free, and we can just return python dictionaries
    @jwt_required()
    def get(self, name):
        item = Item.find_by_name(name)
        return item if item else {'message': 'Item not found'}, 404

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = 'SELECT * FROM items WHERE name = ?'
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()
        if row:
            return {'item': {'name': row[0], 'price': row[1]}}        

    def post(self, name):
        if Item.find_by_name(name):
            # 400 for bad request
            return {'message': 'An item with name {} already exists'.format(name)}, 400

        data = Item.parser.parse_args()
        item = {'name': name, 'price': data['price']}

        # catch potential internal server error
        try:
            Item.insert(item)
        except:
            return {'message': 'An error occurred inserting the item'}, 500

        # apart from 201 status code indicating CREATED,
        # there's also 202 status code indicating ACCEPTED,
        # in this case it means it might take a while before the object
        # is finally created, so we're making sure the client is aware of this delay.
        return item, 201

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = 'INSERT INTO items VALUES (?, ?)'
        cursor.execute(query, (item['name'], item['price']))
        connection.commit()
        connection.close()

    def put(self, name):
        """if the item exists, update the item, if not insert it."""
        data = Item.parser.parse_args()
        item = {'name': name, 'price': data['price']}
        if Item.find_by_name(name):
            # catch potential internal server error
            try:
                Item.update(item)
            except:
                return {'message': 'An error occurred inserting the item'}, 500
        else:
            # catch potential internal server error
            try:
                Item.insert(item)
            except:
                return {'message': 'An error occurred inserting the item'}, 500

        return item

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = 'UPDATE items SET price = ? WHERE name = ?'
        cursor.execute(query, (item['price'], item['name']))
        connection.commit()
        connection.close()

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = 'DELETE FROM items WHERE name = ?'
        cursor.execute(query, (name,))
        connection.commit()
        connection.close()
        return {'message': 'Item deleted'}


class ItemList(Resource):

    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = 'SELECT * FROM items'
        result = cursor.execute(query)
        items = [{'name': name, 'price': price} for name, price in result]
        connection.close()
        return {'items': items}
