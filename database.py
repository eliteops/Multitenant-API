from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///tenants.db')
sessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)
Session = sessionLocal()

Base = declarative_base()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
