import math


class Paginate:

    def __init__(self, query, current_page=1, per_page=10):
        self.query = query
        self.current_page = current_page
        self.per_page = per_page

    @property
    def items(self):
        skip_data = (self.current_page - 1) * self.per_page
        return self.query.skip(skip_data).limit(self.per_page)

    @property
    def total_pages(self):
        return math.ceil(self.query.count() / self.per_page)
