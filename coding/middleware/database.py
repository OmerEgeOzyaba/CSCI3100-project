from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of your database.py file
import os

class Database:
    _instance = None

    _engine = None
    _maker = None
    _session = None

    def __new__(cls):
        if not cls._instance:
            print("Creating Database engine")
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._engine = create_engine(f'postgresql+psycopg2://{os.getenv("PG_USER")}:{os.getenv("PG_PASSWORD")}@{os.getenv("PG_HOST")}:{os.getenv("PG_PORT")}/{os.getenv("PG_DATABASE")}', echo=True)
            cls._instance._maker = sessionmaker(bind=cls._instance._engine)
        return cls._instance
    
    def get_engine(self) -> Engine:
        return self._engine
    
    def get_session(self) -> Session:
        if not self._session:
            print("Creating Database session")
            self._session = self._maker()
        return self._session
    
    def close_session(self):
        if self._session:
            print("Closing Database session")
            self._session.close()
            self._session = None

