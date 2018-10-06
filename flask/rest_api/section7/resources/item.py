from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
from models.item import ItemModel


class Item(Resource):
    """Many APIs are like this, CRUD, create, read, update, delete."""

    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True,
                        help='item price must be passed with the payload')
    parser.add_argument('store_id', type=int, required=True,
                        help='store id must be passed with the payload')

    # we no longer need jsonify as inheriting the Resource
    # class gives us that for free, and we can just return python dictionaries
    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        else:
            return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            # 400 for bad request
            message = 'An item with name {} already exists'.format(name)
            return {'message': message}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        item.save_to_db()

        # apart from 201 status code indicating CREATED,
        # there's also 202 status code indicating ACCEPTED,
        # in this case it means it might take a while before the object
        # is finally created, so we're making sure the client
        # is aware of this delay.
        return item.json(), 201

    def put(self, name):
        """if the item exists, update the item, if not insert it."""
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        # update the price if the item doesn't exist or insert a new item
        if item:
            item.price = data['price']
            item.store_id = data['store_id']
        else:
            item = ItemModel(name, **data)

        item.save_to_db()
        return item.json()

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}


class ItemList(Resource):

    def get(self):
        items = ItemModel.query.all()
        return {'items': [item.json() for item in items]}
