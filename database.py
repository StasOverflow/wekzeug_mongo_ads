import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBClient(metaclass=_Singleton):

    def __init__(self, *args, db_name='test', **kwargs):
        self.connection = MongoClient(*args, **kwargs)
        self.instance = self.connection[db_name]
        self.tables = list()
        self.current_table = None

    def register_table(self, name):
        self.tables.append(self.instance[name])

    def select_table(self, name):
        try:
            self.current_table = self.tables.index(self.instance[name])
            print('Selected table number ', self.current_table)
            return self.tables[self.current_table]
        except Exception as e:
            print(e)

    def get(self, parameter='_id', value=None, table_name=None):
        if table_name is None:
            table = self.tables[self.current_table]
        else:
            try:
                table = self.tables[table_name]
            except Exception as e:
                print(e)
                raise
        ad = table.find_one({parameter: ObjectId(value)})
        return ad

    def insert(self, new_object, table_name=None):
        if table_name is None:
            table = self.tables[self.current_table]
        else:
            try:
                table = self.tables[table_name]
            except Exception as e:
                print(e)
                raise
        table.insert_one(new_object)

    def get_all(self, table_name=None):
        if table_name is None:
            table = self.tables[self.current_table]
        else:
            try:
                table = self.tables[table_name]
            except Exception as e:
                print(e)
                raise
        return table.find()

    def get_ordered_all(self, table_name=None):
        return self.get_all().sort([("created_on", pymongo.DESCENDING)])
