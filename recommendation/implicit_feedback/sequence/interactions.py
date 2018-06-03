

class Interactions:

    def __init__(self, user_ids, item_ids, ratings, timestamps = None, weights = None,
                 num_users = None, num_items = None):
        self.user_ids = user_ids
        self.item_ids = item_ids
        self.ratings = ratings
        self.timestamps = timestamps
        self.weights = weights

        self.num_users = num_users or int(user_ids.max() + 1)
        self.num_items = num_items or int(item_ids.max() + 1)
        self._check()

    def _check(self):
        if self.user_ids.max() >= self.num_users:
            raise ValueError('Maximum user id greater '
                             'than declared number of users.')
        if self.item_ids.max() >= self.num_items:
            raise ValueError('Maximum item id greater '
                             'than declared number of items.')

        num_interactions = len(self)
        for name, value in (('item IDs', self.item_ids),
                            ('ratings', self.ratings),
                            ('timestamps', self.timestamps),
                            ('weights', self.weights)):
            if value is None:
                continue

            if len(value) != num_interactions:
                raise ValueError('Invalid {} dimensions: length '
                                 'must be equal to number of interactions'
                                 .format(name))

    def __repr__(self):
        return ('<Interactions dataset ({num_users} users x {num_items} items '
                'x {num_interactions} interactions)>'
                .format(num_users=self.num_users,
                        num_items=self.num_items,
                        num_interactions=len(self)))

    def __len__(self):
        return len(self.user_ids)
