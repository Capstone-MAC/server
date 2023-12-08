from sqlalchemy import Column, BIGINT, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, BOOLEAN
from database.utility.time_util import TimeUtility
from database.models.results import MACResult
from sqlalchemy.orm.session import Session
from typing import Optional, List, Union
from database.models.base import Base
from database.models.item import Item
from sqlalchemy.sql import func
from datetime import datetime
import traceback
import logging

class Purchase(Base):
    """ Purchase Class
    
    """
    __tablename__ = "purchase"
    
    user_seq = Column(BIGINT, nullable = False, primary_key = False) # 유저 고유 번호
    item_seq = Column(BIGINT, nullable = False, primary_key = False) # 물품 고유 번호
    start_at = Column(DateTime(timezone = True), default = func.now()) # 구매 요청 시작 시간
    end_at = Column(DateTime(timezone = True), default = func.now()) # 구매 완료 시간
    complete = Column(BOOLEAN, default = False) # 상품 구매 완료 여부
    
    __table_args__ = (ForeignKeyConstraint(
        ["item_seq"], ["item.seq"] , ondelete="CASCADE", onupdate="CASCADE"
    ), ForeignKeyConstraint(
        ["user_seq"], ["user.seq"], ondelete = "CASCADE", onupdate = "CASCADE"
    ), PrimaryKeyConstraint("user_seq", "item_seq"),)
    
    def __init__(self, user_seq: int, item_seq: int, start_at: datetime = datetime.now(), end_at: datetime = datetime.now()):
        self.user_seq = user_seq
        self.item_seq = item_seq
        self.start_at = start_at
        self.end_at = end_at
    
    def property(self):
        return {
            "user_seq": self.user_seq,
            "item_seq": self.item_seq,
            "start_at": TimeUtility.parse_time(self.start_at.strftime("%Y/%m/%d %H:%M:%S")),
            "end_at": TimeUtility.parse_time(self.end_at.strftime("%Y/%m/%d %H:%M:%S"))
        }
        
    @staticmethod
    def get_purchase_item_list(db_session: Session, user_seq: int) -> List[Item]:
        try:
            results = db_session.query(Purchase).filter_by(user_seq = user_seq, complete = False).all()
            return list(map(lambda x: Item.get_item_by_item_seq(db_session, x.item_seq).recommend(db_session), results)) #type: ignore
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return []
        
        finally:
            pass