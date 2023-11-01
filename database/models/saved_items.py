from sqlalchemy import Column, BIGINT, DateTime, ForeignKeyConstraint
from sqlalchemy.orm.session import Session
from database.models.base import Base
from sqlalchemy.sql import func
from datetime import datetime
from typing import TypeVar

SavedItems = TypeVar("SavedItems", bound="SavedItems")

class SavedItems(Base):
    __tablename__ = "saved_items"
    
    user_seq = Column(BIGINT, nullable = False, primary_key = True)
    item_seq = Column(BIGINT, nullable = False, primary_key = True)
    saved_at = Column(DateTime(timezone = True),  nullable = False, default = func.now())
    
    __table_args__ = (ForeignKeyConstraint(
        ["user_seq"], ["user.seq"] , ondelete="CASCADE", onupdate="CASCADE"
    ),)
    
    def __init__(self, user_seq: int, item_seq: int, saved_at: datetime = datetime.now()):
        self.user_seq = user_seq
        self.item_seq = item_seq
        self.saved_at = saved_at
        
    @property
    def info(self):
        return {
            "user_seq": self.user_seq,
            "item_seq": self.item_seq,
            "saved_at": self.saved_at.strftime("%Y/%m/%d %H:%M:%S") #type: ignore
        }
    
    @staticmethod
    def get_saved_items_by_user_seq(db_session: Session, user_seq: int):
        return list(db_session.query(SavedItems).filter_by(user_seq = user_seq).all())
    
    @staticmethod
    def get_like_user_by_item_seq(db_session: Session, item_seq: int):
        return list(db_session.query(SavedItems).filter_by(item_seq = item_seq).all())