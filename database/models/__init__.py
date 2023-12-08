from database.conn import EngineConn
from .item_images import ItemImages
from .saved_items import SavedItems
from .category import Category
from .purchase import Purchase
from .user import User
from .item import Item

def create_table(engine: EngineConn):
    tables = [User, SavedItems, Category, Item, ItemImages, Purchase]
    for table in tables:
        table.__table__.create(bind = engine.engine, checkfirst = True)