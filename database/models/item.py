from sqlalchemy import Column, BIGINT, TEXT, INT, DateTime, BOOLEAN, ForeignKeyConstraint
from typing import Optional, TypeVar, List, Any, Dict
from database.utility.time_util import TimeUtility
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
    user_seq = Column(BIGINT, nullable = False) # 미들맨 고유 번호
    name = Column(TEXT, nullable = False) # 아이템 이름
    cnt = Column(INT, nullable = True, default = -1) # 아이템 잔여 개수
    price = Column(INT, nullable = True, default = -1) # 아이템 가격
    description = Column(TEXT, nullable = True, default = "") # 아이템 설명
    views = Column(INT, nullable = True, default = 0) # 아이템 조회수
    created_at = Column(DateTime, nullable = True, default = func.now()) # 아이템 등록 날짜
    category_seq = Column(BIGINT, nullable = False) # 카테고리 고유 번호
    purchase_type = Column(BOOLEAN, default = False) # 상품 구매 상태 여부
    
    __table_args__ = (ForeignKeyConstraint(
        ["category_seq"], ["category.seq"] , ondelete="CASCADE", onupdate="CASCADE"
    ),)
    
    def info(self, db_session: Session):    
        from database.models.user import User
        return {
            "seq": self.seq,
            "middleman_name": User.convert_seq_to_name(db_session, self.user_seq), #type: ignore
            "name": self.name,
            "category": Category.convert_member(db_session, seq = self.category_seq), # type: ignore
            "cnt": format(self.cnt, ','),
            "price": format(self.price, ','),
            "description": self.description,
            "views": self.views,
            "saved_cnt": len(SavedItems.get_saved_items_by_item_seq(db_session, self.seq)), #type: ignore
            "created_at": TimeUtility.parse_time(self.created_at.strftime("%Y/%m/%d %H:%M:%S")),
            "images": ItemImages.get_all_image_path(db_session, self.seq) #type: ignore
        }
        
    def recommend(self, db_session: Session):
        return {
            "seq": self.seq,
            "name": self.name,
            "created_at": TimeUtility.parse_time(self.created_at.strftime("%Y/%m/%d %H:%M:%S")),
            "price": self.price,
            "saved_cnt": len(SavedItems.get_saved_items_by_item_seq(db_session, self.seq)), #type: ignore
            "image_path": ItemImages.get_image_path(db_session, self.seq, 0) #type: ignore
        }
    
    def __init__(self, name: str, category_seq: int, user_seq: int, seq: Optional[int] = None, cnt: Optional[int] = None, price: Optional[int] = None, description: Optional[str] = None, views: Optional[int] = None, created_at: datetime = datetime.now(), purchase_type: Optional[bool] = None):
        self.name = name
        self.category_seq = category_seq
        self.user_seq = user_seq
        self.seq = seq
        self.cnt = cnt
        self.price = price
        self.description = description
        self.views = views
        self.created_at = created_at
        self.purchase_type = purchase_type
       
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
            
            items = db_session.query(Item).filter_by(purchase_type = False).order_by(Item.views.desc()).all()[start: start + count] #type: ignore
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
            
            items = db_session.query(Item.name).filter(Item.name.ilike(f"%{search_value}%"), Item.purchase_type == False).order_by(Item.seq.asc()).all() #type: ignore
            return [dict(t) for t in {tuple(d.items()) for d in list(map(lambda x: {"name": x[0]}, items))}]
            
        except ValueError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
    
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        
    @staticmethod
    def search_detail_items(db_session: Session, search_value: str, start: int, count: int) -> Optional[List[Dict[str, Any]]]:
        try:
            if count > 50 or count < 1:
                raise ValueError("count (max: 50, min: 1)")
            
            if start < 0:
                raise ValueError("start (min: 0)")
            
            items = db_session.query(Item).filter(Item.name.ilike(f"%{search_value}%"), Item.purchase_type == False).order_by(Item.seq.asc()).all() #type: ignore
            return list(map(lambda x: x.recommend(db_session), items))
        
        except ValueError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
    
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
       
    @staticmethod
    def insert_item_info(db_session: Session, user_seq: int, name: str, category: str, cnt: int, price: int, description: str) -> MACResult:
        try:
            category_seq = Category.convert_member(db_session, name = category)
            if category_seq is None:
                return MACResult.ENTITY_ERROR
            
            if isinstance(category_seq, str):
                return MACResult.INTERNAL_SERVER_ERROR
            
            else:
                item = Item(name = name, user_seq = user_seq, category_seq = category_seq, cnt = cnt, price = price, description = description)
                db_session.add(item)
                db_session.commit()
                return MACResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
                
    def update_item_info(self, db_session: Session, user_seq: int, name: Optional[str] = None, cnt: Optional[int] = None, price: Optional[int] = None, description: Optional[str] = None, views: Optional[int] = None) -> MACResult:
        try:
            if any(arg is not None for arg in [name, cnt, price, description, views]):
                item = db_session.query(Item).filter_by(seq = self.seq)
                if item.first().user_seq != user_seq: # type: ignore
                    return MACResult.FORBIDDEN
                    
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

    def delete_item(self, db_session: Session, user_seq: int) -> MACResult:
        try:
            if user_seq != self.user_seq:
                return MACResult.FORBIDDEN
            
            result = db_session.query(Item).filter_by(seq = self.seq).delete()
            db_session.commit()
            return MACResult.SUCCESS if result == 1 else MACResult.FAIL
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
    
    def purchase_request(self, db_session: Session) -> MACResult:
        try:
            db_session.query(Item).filter_by(item_seq = self.seq).update({"purchase_type": True})
            return MACResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR