from flask_restful import Resource
from models.store import StoreModel


class Store(Resource):

    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        else:
            return {'message': 'Store not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            message = 'Store with name {} already exists'.format(name)
            return {'Message': message}, 400

        store = StoreModel(name)
        store.save_to_db()
        return store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {'Message': 'Store deleted'}


class StoreList(Resource):

    def get(self):
        stores = StoreModel.query.all()
        return {'stores': [store.json() for store in stores]}
