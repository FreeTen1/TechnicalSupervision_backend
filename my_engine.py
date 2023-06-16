
from config import MYSQL
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import Session


engine = create_engine(f"mysql+mysqlconnector://{MYSQL['user']}:{MYSQL['password']}@{MYSQL['host']}/{MYSQL['database']}", encoding='utf8', echo=False)
my_session = sessionmaker(bind=engine)
my_metadata = MetaData(bind=engine)


@contextmanager
def session_scope():
    session: Session = my_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

