from sqlalchemy import Column, BIGINT, String
from sqlalchemy.orm.session import Session
from typing import Optional, List, Union
from database.models.base import Base
import traceback
import logging

class Category(Base):
    """ Category Class
    
    """
    __tablename__ = "category"
    
    seq = Column(BIGINT, nullable = False, autoincrement = True, primary_key = True) # 카테고리 일련번호
    name = Column(String(10), nullable = False, unique = True) # 카테고리 이름
    
    def __init__(self, name: str, seq: Optional[int] = None):
        self.seq = seq
        self.name = name
    
    @staticmethod
    def setting(db_session: Session) -> None:
        try:
            categories = "디지털 기기, 생활 가전, 패션, 보석, 명품, 취미·생활, 뷰티·미용, 반려동물, 식물, 도서, 기타".split(", ")
            for category in categories:
                obj = Category(category)
                db_session.add(obj)
            
            db_session.commit()
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            
        
    @staticmethod
    def get_all_category_name(db_session: Session) -> Optional[List[str]]:
        try:
            result = db_session.query(Category.name).all()
            categories = list(map(lambda x: x[0], result))
            return categories
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        
    @staticmethod
    def convert_member(db_session: Session, name: Optional[str] = None, seq: Optional[int] = None) -> Optional[Union[int, str]]:
        assert [name, seq].count(None), "name과 seq중 값 하나만 있어야 합니다."
        try:
            if name is not None:
                result = db_session.query(Category.seq).filter_by(name = name).first()
                
            else:
                result = db_session.query(Category.name).filter_by(seq = seq).first()
                
            return None if result is None else result[0]
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None
        