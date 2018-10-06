from extensions import db


class ItemModel(db.Model):

    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)

    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))

    # different value for the lazy argument
    # https://medium.com/@ns2586/sqlalchemys-relationship-and-lazy-parameter-4a553257d9ef
    store = db.relationship('StoreModel', backref='items', lazy=True)

    def __init__(self, name, price, store_id):
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self):
        return {'name': self.name, 'price': self.price}

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        """"insert or update ItemModel to db."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
