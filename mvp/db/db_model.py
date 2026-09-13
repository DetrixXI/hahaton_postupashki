from sqlalchemy import Integer, event, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from config import settings

DB_URL = settings.database.sync_url

class DB_helper():
    def __init__(self):
        self.engine = create_engine(url= DB_URL,
                                    pool_size= 3, max_overflow= 5)
        self.session_gen = sessionmaker(bind=self.engine, autocommit=False,
                                            autoflush=False, expire_on_commit=False)

        @event.listens_for(self.engine, "connect")
        def pragma_for_fk(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
    
    def get_session(self):
        with self.session_gen() as ses:
            yield ses
    

db_helper = DB_helper()

class Base(DeclarativeBase):
    __abstract__ = True
