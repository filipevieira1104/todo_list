from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"

def get_engine():
    return create_engine(
        SQLALCHEMY_DATABASE_URL,
    )

def get_session():
    Session = sessionmaker(
        autocommit = False,
        autoflush=False,
        bind=get_engine(),
    )
    try:
        session = Session()
        yield session
    finally:
        session.close()    