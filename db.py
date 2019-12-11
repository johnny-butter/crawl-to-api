import pymongo
from elasticsearch import Elasticsearch


class db:

    def __init__(self, url, port, db_name, table_name, username=None, pwd=None):
        self.url = url
        self.port = port
        self.db_name = db_name
        self.table_name = table_name
        self.username = username
        self.pwd = pwd

        self.connect()

    def connect(self):
        raise NotImplementedError

    def save(self, data):
        raise NotImplementedError


class Mongo(db):

    def connect(self):
        client = pymongo.MongoClient(host=self.url, port=self.port)
        self.table = client[self.db_name][self.table_name]

    def save(self, data):
        self.table.insert_one(data)

    def client(self):
        return self.table


class Elastic(db):

    def connect(self):
        self.es = Elasticsearch(
            hosts=[
                {
                    'host': self.url,
                    'port': self.port,
                }
            ],
        )

    def save(self, data):
        self.es.index(self.db_name, data)

    def client(self):
        return self.es
