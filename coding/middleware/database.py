from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

class Database:
    _instance = None
    _maker = None
    _session = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = create_engine(f'postgresql+psycopg2://{os.getenv("PG_USER")}:{os.getenv("PG_PASSWORD")}@{os.getenv("PG_HOST")}:{os.getenv("PG_PORT")}/{os.getenv("PG_DATABASE")}', echo=True)
        return cls._instance
    
    def get_session(self):
        if not self._maker:
            self._maker = sessionmaker(bind=self._instance)
        if not self._session:
            self._session = self._maker()
        return self._session
    
    def close_session(self):
        if self._session:
            self._session.close()
            self._session = None

