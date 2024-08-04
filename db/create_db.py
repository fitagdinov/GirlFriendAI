from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import database_exists, create_database, drop_database

from db.table import Base
from db.utils import get_engine


def create_db():
    engine = get_engine()

    # creates empty db if not exists

    if not database_exists(engine.url):
        create_database(engine.url)

    conn = engine.connect()

    # creates schemas if not exists
    for schema in ['general', 'service']:
        conn.execute(CreateSchema(schema, if_not_exists=True))
        conn.commit()

    # create all tables
    Base.metadata.create_all(engine)
    conn.close()

def delete_db():
    engine = get_engine()
    if database_exists(engine.url):
        drop_database(engine.url)
        print("DROP BD")
if __name__ == "__main__":
    create_db()
