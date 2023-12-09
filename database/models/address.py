from sqlalchemy import Column, String, BIGINT, TEXT, BOOLEAN, ForeignKeyConstraint, PrimaryKeyConstraint
from database.models.results import MACResult
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from database.models.base import Base
from pydantic import BaseModel
from typing import Optional
import traceback
import logging


class AddressBody(BaseModel):
    road_full_addr: str
    eng_addr: str
    zip_no: str
    addr_detail: Optional[str]
    adm_cd: str
    rn_mgt_sn: str
    bg_mgt_sn: str
    si_nm: str
    sgg_nm: str
    emd_nm: str
    rn: str


class Address(Base):
    """ Address Class
    
    """
    
    __tablename__ = "address"
    
    user_seq = Column(BIGINT, nullable = False)
    is_default = Column(BOOLEAN, nullable = True, default = False)
    road_full_addr = Column(String(255), nullable = False)
    eng_addr = Column(TEXT, nullable = False)
    zip_no = Column(TEXT, nullable = False)
    addr_detail = Column(TEXT, nullable = True, default = None)
    adm_cd = Column(TEXT, nullable = False)
    rn_mgt_sn = Column(TEXT, nullable = False)
    bg_mgt_sn = Column(TEXT, nullable = False)
    si_nm = Column(TEXT, nullable = False)
    sgg_nm = Column(TEXT, nullable = False)
    emd_nm = Column(TEXT, nullable = False)
    rn = Column(TEXT, nullable = False)
    
    __table_args__ = (ForeignKeyConstraint(
        ["user_seq"], ["user.seq"] , ondelete="CASCADE", onupdate="CASCADE"
    ), PrimaryKeyConstraint("user_seq", "road_full_addr"),)
    
    def __init__(self, user_seq: int, road_full_addr: str, eng_addr: str, zip_no: str, adm_cd: str, rn_mgt_sn: str, bg_mgt_sn: str, si_nm: str, sgg_nm: str, emd_nm: str, rn: str, addr_detail: Optional[str] = None):
        self.user_seq = user_seq
        self.road_full_addr = road_full_addr
        self.eng_addr = eng_addr
        self.zip_no = zip_no
        self.adm_cd = adm_cd
        self.rn_mgt_sn = rn_mgt_sn
        self.bg_mgt_sn = bg_mgt_sn
        self.si_nm = si_nm
        self.sgg_nm = sgg_nm
        self.emd_nm = emd_nm
        self.rn = rn
        self.addr_detail = addr_detail
    
    def info(self):
        data = self.__dict__
        del data["_sa_instance_state"]
        return data
    
    @staticmethod
    def insert_address(db_session: Session, user_seq: int, road_full_addr: str, eng_addr: str, zip_no: str, adm_cd: str, rn_mgt_sn: str, bg_mgt_sn: str, si_nm: str, sgg_nm: str, emd_nm: str, rn: str, addr_detail: Optional[str] = None):
        try:
            address_obj = Address(user_seq, road_full_addr, eng_addr, zip_no, adm_cd, rn_mgt_sn, bg_mgt_sn, si_nm, sgg_nm, emd_nm, rn, addr_detail)
            db_session.add(address_obj)
            
            return MACResult.SUCCESS

        except IntegrityError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.CONFLICT
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
            
        finally:
            db_session.commit()
            
    @staticmethod
    def delete_address(db_session: Session, user_seq: int, road_full_addr: str):
        try:
            db_session.query(Address).filter_by(user_seq = user_seq, road_full_addr = road_full_addr).delete()
            return MACResult.SUCCESS
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.INTERNAL_SERVER_ERROR
        
        finally:
            db_session.commit()
            
    @staticmethod
    def get_address(db_session: Session, user_seq: int):
        try:
            addresses = db_session.query(Address).filter_by(user_seq = user_seq).all()
            return list(map(lambda x: x.info(), addresses))
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return []
        
    @staticmethod
    def set_default_address(db_session: Session, user_seq: int, road_full_addr: str):
        try:
            db_session.query(Address).filter_by(user_seq = user_seq, road_full_addr = road_full_addr).update({"is_default": True})
            db_session.query(Address).filter_by(user_seq = user_seq).filter(Address.road_full_addr != road_full_addr).update({"is_default": False}) # type: ignore
            return MACResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return MACResult.FAIL
        
    @staticmethod
    def get_default_address(db_session: Session, user_seq: int):
        try:
            addresses = db_session.query(Address).filter_by(user_seq = user_seq, is_default = True).all()
            return list(map(lambda x: x.info(), addresses))
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return []