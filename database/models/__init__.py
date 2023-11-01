from database.conn import EngineConn
from .saved_items import SavedItems
from .user import User

tables = [User, SavedItems]

def create_table(engine: EngineConn):
    tables = [User, SavedItems]
    for table in tables:
        table.__table__.create(bind = engine.engine, checkfirst = True)