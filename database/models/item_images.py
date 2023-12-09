from sqlalchemy import Column, BIGINT, TEXT, ForeignKeyConstraint, PrimaryKeyConstraint
from database.models.results import MACResult
from sqlalchemy.orm.session import Session
from typing import Optional, List, Dict
from database.models.base import Base
import traceback
import logging
import uuid
import os

class ItemImages(Base):
    __tablename__ = "item_images"
    
    item_seq = Column(BIGINT, nullable = False, autoincrement = True, primary_key = False) # 물품 고유 번호
    index = Column(BIGINT, nullable = True, default = 0) # 물품 이미지 인덱스
    path = Column(TEXT, default = None, nullable = True) # 이미지 경로
    
    __table_args__ = (ForeignKeyConstraint(
        ["item_seq"], ["item.seq"] , ondelete="CASCADE", onupdate="CASCADE"
    ), PrimaryKeyConstraint("item_seq", "index"),)
    
    def __init__(self, item_seq: int, index: int, path: str):
        self.item_seq = item_seq
        self.index = index
        self.path = path
        
    @staticmethod
    def get_all_image_path(db_session: Session, item_seq: int) -> Optional[List[Dict[str, str]]]:
        try:
            result = db_session.query(ItemImages.path, ItemImages.index).filter_by(item_seq = item_seq).all()
            
            if result is None:
                return None
            
            return sorted(list(map(lambda x: {"path": x[0], "index": x[1]}, result)), key = lambda x: x["index"]) #type: ignore
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        
    @staticmethod
    def get_image_path(db_session: Session, item_seq: int, index: int) -> Optional[str]:
        try:
            result = db_session.query(ItemImages.path).filter_by(item_seq = item_seq, index = index).first()
            
            if result is None:
                return None
            
            return result[0]
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
            
    @staticmethod
    def insert_image(db_session: Session, item_seq: int, index: int, image: bytes) -> MACResult:
        try:
            file_name = f"{str(uuid.uuid4())}.jpg"
            with open(os.path.join("images", file_name), "wb") as fp:
                fp.write(image)
            
            item_images = ItemImages(item_seq, index, os.path.join("images", file_name))
            if db_session.query(ItemImages.index).filter_by(item_seq = item_seq, index = index).first() is not None:
                return MACResult.CONFLICT
            db_session.add(item_images)
            
            db_session.commit()
            return MACResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
        
    @staticmethod
    def delete_image(db_session: Session, item_seq: int, file_path: str) -> MACResult:
        try:
            obj = db_session.query(ItemImages).filter_by(item_seq = item_seq, file_path = file_path).first()
            db_session.query(ItemImages).delete(obj)
            db_session.commit()
            return MACResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR