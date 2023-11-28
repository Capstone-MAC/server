from sqlalchemy import Column, BIGINT, TEXT, INT, DateTime, ForeignKeyConstraint
from typing import Optional, TypeVar, List, Any, Dict
from database.models.item_images import ItemImages
from database.models.saved_items import SavedItems
from database.models.category import Category
from database.models.results import MACResult
from sqlalchemy.orm.session import Session
from database.models.base import Base
from sqlalchemy.sql import func
from datetime import datetime
import traceback
import logging

Item = TypeVar("Item", bound="Item")

class Item(Base):
    """Item Class
    
    """
    __tablename__ = "item"
    
    seq = Column(BIGINT, nullable = False, autoincrement = True, primary_key = True) # 아이템 일련번호
    name = Column(TEXT, nullable = False) # 아이템 이름
    cnt = Column(INT, nullable = True, default = -1) # 아이템 잔여 개수
    price = Column(INT, nullable = True, default = -1) # 아이템 가격
    description = Column(TEXT, nullable = True, default = "") # 아이템 설명
    views = Column(INT, nullable = True, default = 0) # 아이템 조회수
    created_at = Column(DateTime, nullable = True, default = func.now()) # 아이템 등록 날짜
    category_seq = Column(BIGINT, nullable = False) # 카테고리 고유 번호
    
    __table_args__ = (ForeignKeyConstraint(
        ["category_seq"], ["category.seq"] , ondelete="CASCADE", onupdate="CASCADE"
    ),)
    
    def info(self, db_session: Session):
        return {
            "seq": self.seq,
            "name": self.name,
            "category": Category.convert_member(db_session, seq = self.category_seq), # type: ignore
            "cnt": format(self.cnt, ','),
            "price": format(self.price, ','),
            "description": self.description,
            "views": self.views,
            "saved_cnt": len(SavedItems.get_saved_items_by_item_seq(db_session, self.seq)), #type: ignore
            "created_at": Item.parse_time(self.created_at.strftime("%Y/%m/%d %H:%M:%S")),
            "images": ItemImages.get_all_image_path(db_session, self.seq) #type: ignore
        }
        
    def recommend(self, db_session: Session):
        return {
            "seq": self.seq,
            "name": self.name,
            "created_at": Item.parse_time(self.created_at.strftime("%Y/%m/%d %H:%M:%S")),
            "price": self.price,
            "saved_cnt": len(SavedItems.get_saved_items_by_item_seq(db_session, self.seq)), #type: ignore
            "image_path": ItemImages.get_image_path(db_session, self.seq, 0) #type: ignore
        }
    
    def __init__(self, name: str, category_seq: int, seq: Optional[int] = None, cnt: Optional[int] = None, price: Optional[int] = None, description: Optional[str] = None, views: Optional[int] = None, created_at: datetime = datetime.now()):
        self.name = name
        self.category_seq = category_seq
        self.seq = seq
        self.cnt = cnt
        self.price = price
        self.description = description
        self.views = views
        self.created_at = created_at
        
    @staticmethod
    def parse_time(created_at: str) -> str:
        time = datetime.strptime(created_at, "%Y/%m/%d %H:%M:%S")
        time_diff = (datetime.now() - time)
        seconds = time_diff.seconds
        days = time_diff.days
        if seconds < 60:
            return f"{seconds}초 전"
        
        elif seconds < 60 * 60:
            return f"{seconds // 60}분 전"
        
        elif days < 1:
            return f"{seconds // 60 // 60}시간 전"
        
        else:
            if days <= 3:
                return f"{days}일 전"
            
            else:
                return time.strftime("%Y년 %m월 %d일")
       
    @staticmethod
    def get_item_by_item_seq(db_session: Session, seq: int) -> Optional[Item]:
        """
        Parameters:
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            seq (int | None): 아이템 고유 번호를 통해 정보를 불러옴 \n
            
        Returns:
            Item: 아이템 정보를 담은 Item 객체 \n
            None: 정보를 불러오는데 실패 \n
        """
        
        try:
            item = db_session.query(Item).filter_by(seq = seq).first()
            if item is None:
                return None
            del item.__dict__["_sa_instance_state"]
            return Item(**item.__dict__)
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        
    @staticmethod
    def get_recommended_item(db_session: Session, start: int, count: int) -> Optional[List[Item]]:
        try:
            if count > 50 or count < 0:
                raise ValueError("count (max: 50, min: 0)")
            
            if start < 0:
                raise ValueError("start (min: 0)")
            
            items = db_session.query(Item).order_by(Item.views.desc()).all()[start: start + count] #type: ignore
            if items is None:
                return None
            
            else:
                return list(map(lambda x: x.recommend(db_session), items)) # type: ignore
        
        except ValueError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        
    @staticmethod
    def search_items(db_session: Session, search_value: str, start: int, count: int) -> Optional[List[Dict[str, Any]]]:
        try:
            if count > 50 or count < 1:
                raise ValueError("count (max: 50, min: 1)")
            
            if start < 0:
                raise ValueError("start (min: 0)")
            
            items = db_session.query(Item.seq, Item.name).filter(Item.name.ilike(f"%{search_value}%")).order_by(Item.seq.asc()).all() #type: ignore
            return list(map(lambda x: {"seq": x[0], "name": x[1]}, items))
        
        except ValueError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
    
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        
    @staticmethod
    def search_detail_items(db_session: Session, search_value: str, start: int, count: int) -> Optional[List[dict[str, Any]]]:
        try:
            if count > 50 or count < 1:
                raise ValueError("count (max: 50, min: 1)")
            
            if start < 0:
                raise ValueError("start (min: 0)")
            
            items = db_session.query(Item).filter(Item.name.ilike(f"%{search_value}%")).order_by(Item.seq.asc()).all() #type: ignore
            return list(map(lambda x: x.recommend(db_session), items))
        
        except ValueError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
    
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
       
    @staticmethod
    def insert_item_info(db_session: Session, name: str, category: str, cnt: int, price: int, description: str) -> MACResult:
        try:
            category_seq = Category.convert_member(db_session, name = category)
            if category_seq is None:
                return MACResult.ENTITY_ERROR
            
            if isinstance(category_seq, str):
                return MACResult.INTERNAL_SERVER_ERROR
            
            else:
                item = Item(name = name, category_seq = category_seq, cnt = cnt, price = price, description = description)
                db_session.add(item)
                db_session.commit()
                return MACResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
                
    def update_item_info(self, db_session: Session, name: Optional[str] = None, cnt: Optional[int] = None, price: Optional[int] = None, description: Optional[str] = None, views: Optional[int] = None) -> MACResult:
        try:
            if any(arg is not None for arg in [name, cnt, price, description, views]):
                item = db_session.query(Item).filter_by(seq = self.seq)
                if name:
                    item.update({"name": name})
                
                if cnt:
                    item.update({"cnt": cnt})
                
                if price:
                    item.update({"price": price})
                
                if description:
                    item.update({"description": description})
                
                if views:
                    item.update({"views": views})
                    
                db_session.commit()
                return MACResult.SUCCESS
            
            else:
                return MACResult.FAIL
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR

    def delete_item(self, db_session: Session) -> MACResult:
        try:
            result = db_session.query(Item).filter_by(seq = self.seq).delete()
            db_session.commit()
            return MACResult.SUCCESS if result == 1 else MACResult.FAIL
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
        