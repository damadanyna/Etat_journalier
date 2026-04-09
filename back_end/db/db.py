# db.py
import os

from sqlalchemy import create_engine

from config import load_project_env


load_project_env()

class DB:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost/dfe_test')
        self.engine = create_engine(self.db_url, pool_size=5, max_overflow=10)

    def connect(self):
        return self.engine.connect()


 