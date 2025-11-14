# db.py
from sqlalchemy import create_engine

class DB:
    def __init__(self):
        self.db_url = 'mysql+pymysql://root:@localhost/dfe_test'
        self.engine = create_engine(self.db_url, pool_size=5, max_overflow=10)

    def connect(self):
        return self.engine.connect()
