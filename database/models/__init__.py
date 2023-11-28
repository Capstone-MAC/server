from database.conn import EngineConn
from .saved_items import SavedItems
from .category import Category
from .user import User
from .item import Item

def create_table(engine: EngineConn):
    tables = [User, SavedItems, Category, Item]
    for table in tables:
        table.__table__.create(bind = engine.engine, checkfirst = True)