from sqlalchemy import Column, TEXT, BIGINT, String, DateTime
from typing import List, Optional, TypeVar, Dict, Any
from database.models.saved_items import SavedItems
from sqlalchemy.orm.session import Session
from database.models.base import Base
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import traceback
import logging
import bcrypt
import uuid
import os

User = TypeVar("User", bound="User")

class UserResult(Enum):
    """ 유저가 어떤 행동을 할 때, 결과를 클래스로 구현

    Parameters:
        SUCCESS (200): 성공 \n
        FAIL (401): 실패 \n
        FORBIDDEN (403): 금지됨 \n
        NOTFOUND (404): 찾을 수 없음 \n
        TIME_OUT (408): 세션 만료됨 \n
        CONFLICT (409): 데이터 충돌됨 \n
        INTERNAL_SERVER_ERROR (500): 서버 내부 에러 \n
    """
    SUCCESS = 200
    FAIL = 401
    FORBIDDEN = 403
    NOTFOUND = 404
    TIME_OUT = 408
    CONFLICT = 409
    VALIDATION_ERROR = 422
    INTERNAL_SERVER_ERROR = 500
    
    
class IDPWDModel(BaseModel):
    """ 기본적인 ID, Password를 갖는 클래스, 보안을 위해 사용
    
    """
    user_id: str
    password: str
        
        
class SignUpModel(IDPWDModel):
    """ 유저가 회원가입을 할 때, 보안을 위해 사용되는 클래스
    
    """
    name: str
    email: str
    phone: str
    idnum: str
    
    
class SignoutModel(IDPWDModel):
    """ 유저가 회원탈퇴를 할 때, 보안을 위해 사용되는 클래스
    
    """


class LoginModel(IDPWDModel):
    """ 유저가 로그인을 할 때, 보안을 위해 사용되는 클래스
    
    """
    
class ForgotPasswordModel(IDPWDModel):
    """ 유저가 비밀번호를 변경 할 떄, 보안을 위해 사용되는 클래스
    
    """


class User(Base):
    """ User class
    
    """
    
    __tablename__ = "user"
    
    seq = Column(BIGINT, nullable = False, autoincrement = True, primary_key = True) # 유저 일련번호
    user_id = Column(String(15), nullable = False, unique = True) # 유저 아이디
    password = Column(String(60), nullable = False) # 유저 비밀번호
    name = Column(String(10), nullable = False) # 유저 이름
    email = Column(String(50), nullable = False, unique = True) # 유저 이메일
    phone = Column(String(13), nullable = False) # 유저 핸드폰 번호
    profile = Column(TEXT, nullable = True, default = None) # 유저 프로필 이미지 경로
    idnum = Column(String(14), nullable = False, unique = True) # 주민등록번호
    created_at = Column(DateTime(timezone = True), default = func.now()) # 회원가입 시간
    password_update_at = Column(DateTime(timezone = True), default = func.now()) # 비밀번호 업데이트 시간
    login_at = Column(DateTime(timezone = True), default = func.now()) # 마지막 로그인 시간
    logout_at = Column(DateTime(timezone = True), default = func.now()) # 마지막 로그아웃 시간
    
    
    @property 
    def info(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "idnum": self.idnum,
            "profile": self.profile,
            "created_at": self.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            "password_update_date": self.password_update_at.strftime("%Y/%m/%d %H:%M:%S"),
            "login_at": self.login_at.strftime("%Y/%m/%d %H:%M:%S"), #type: ignore
            "logout_at": self.logout_at.strftime("%Y/%m/%d %H:%M:%S")  #type: ignore
        }
    
    def __init__(self, user_id: str, password: str, name: str, email: str, phone: str, idnum: str, seq: Optional[int] = None, profile: Optional[str] = None, created_at: datetime = datetime.now(), password_update_at: datetime = datetime.now(), login_at: datetime = datetime.now(), logout_at: datetime = datetime.now()) -> None:
        self.seq = seq
        self.user_id = user_id
        self.password = password
        self.name = name
        self.email = email
        self.phone = phone
        self.profile = profile
        self.idnum = idnum
        self.created_at = created_at
        self.password_update_at = password_update_at
        self.login_at = login_at
        self.logout_at = logout_at
        
    @staticmethod
    def _load_user_info(db_session: Session, seq: Optional[int] = None, user_id: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        """
        Parameters:
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            seq (int | None): 사용자 고유 번호를 통해 정보를 불러옴 \n
            user_id (str | None): 사용자 아이디를 통해 정보를 불러옴 \n
            email (str | None): 사용자 이메일을 통해 정보를 불러옴 \n
            
        Returns:
            User: 사용자 정보를 담은 User 객체 \n
            None: 정보를 불러오는데 실패 \n
        """
        try:
            result = None
            query = db_session.query(User)
            if seq:
                result = query.filter_by(seq = seq).all()
                
            if user_id:
                result = query.filter_by(user_id = user_id).all()
                
            if email:
                result = query.filter_by(email = email).all()
                
            if result is None:
                return None
            
            user = result[0]
            del user.__dict__["_sa_instance_state"]
            return User(**user.__dict__)
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None


    def _check_exsit_session(self, session: Dict[str, Any]) -> bool:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            
        Returns:
            True: 세션에 아이디가 존재 \n
            False: 세션에 아이디가 존재하지 않음 \n
        """

        try:
            return self.user_id in session.keys()
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return False
        
    @staticmethod
    def check_duplicate(db_session: Session, user_id: Optional[str] = None, email: Optional[str] = None) -> UserResult:
        """
        Parameters:
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            user_id (str | None): 유저가 회원가입 할 때 중복 체크 하는 아이디. \n
            email (str | None): 유저가 회원가입 할 때 중복 체크 하는 이메일. \n
            
        Returns:
            UserResult.SUCCESS: 아이디 또는 이메일 사용 가능! \n
            UserResult.CONFLICT: 아이디 또는 이메일이 중복 됨! \n
            UserResult.VALIDATION_ERROR: 아이디 또는 이메일만 입력 가능! \n
            UserResult.INTERNAL_SERVER_ERROR: 중복 체크 도중 서버 코드 에러 발생! (에러 문구 확인) \n
        """
        
        try:
            result = None
            if user_id:
                result = db_session.query(User).filter_by(user_id = user_id).all()
            
            if email:
                result = db_session.query(User).filter_by(email = email).all()
            
            if user_id and email:
                return UserResult.VALIDATION_ERROR
            
            return UserResult.SUCCESS if len(result) == 0 else UserResult.CONFLICT # type: ignore

        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
    
    @staticmethod
    def signup(db_session: Session, user_id: str, password: str, name: str, email: str, phone: str, idnum: str) -> UserResult:
        """
        Parameters:
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            user_id (str): 유저가 회원가입 할 때 사용하는 아이디, 중복 체크를 먼저 한 후에 사용. \n
            password (str): 유저가 회원가입 할 때 사용하는 비밀번호, 클라이언트에서 암호화 하여 전송. \n
            name (str): 유저의 이름 (성을 포함한 3글자). \n
            email (str): 유저의 이메일. \n
            phone (str): 유저의 폰 (-를 제외한 문자열 (예시: 010-3347-5079)). \n
            idnum (str): 유저의 주민등록 번호 (-를 제외한 문자열 (예시: 021123-3214325)). \n
            
        Returns:
            UserResult.SUCCESS: 회원가입에 성공! \n
            UserResult.CONFLICT: 아이디 또는 이메일이 중복됩니다! \n
            UserResult.INTERNAL_SERVER_ERROR: 회원가입하는데 서버 코드에 에러가 발생! (에러 문구 확인) \n
        """
        try:
            
            if User.check_duplicate(db_session, user_id = user_id) == UserResult.CONFLICT and User.check_duplicate(db_session, email = email) == UserResult.CONFLICT:
                return UserResult.CONFLICT
            
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            user = User(user_id = user_id, password = hashed_password, name = name, email = email, phone = phone, idnum = idnum)
            db_session.add(user)
            db_session.commit()
            return UserResult.SUCCESS
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
    
    def signout(self, db_session: Session, session: Dict[str, Any]) -> UserResult:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            session (Dict[str, Any]): 세션이 존재하는지 확인하기 위한 Session. \n
            user_id (str): 유저가 회원탈퇴를 하기 위해 데이터베이스에서 조회하기 위한 아이디. \n
            password (str): 유저가 회원탈퇴를 할 때, 본인은증을 하기 위한 비밀번호. \n
            
        Returns:
            UserResult.SUCCESS: 회원탈퇴에 성공! \n
            UserResult.FAIL: 회원탈퇴에 실패. \n
            UserResult.TIME_OUT: 세션이 만료됨. \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러.\n
        """
        if not self._check_exsit_session(session):
            return UserResult.TIME_OUT
        
        try:
            db_session.query(User).filter_by(seq = self.seq).delete()
            db_session.commit()
            return UserResult.SUCCESS
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        
    @staticmethod
    def login(db_session: Session, session: Dict[str, Any], user_id: str, password: str) -> UserResult:
        """
        Parameters:
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            session (Dict[str, Any]): 유저 로그인을 제어하기 위한 Session \n
            user_id (str): 유저가 로그인 할 때 사요하는 아이디. \n
            password (str): 유저가 로그인 할 떄 사용하는 비밀번호, 클라이언트에서 암호화 하여 전송. \n
            
        Returns:
            UserResult.SUCCESS: 로그인 성공. \n
            UserResult.FAIL: 로그인 실패. \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """
        
        try:
            user = User._load_user_info(db_session, user_id = user_id)
            if user:
                if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                    db_session.query(User).update({"login_at": datetime.now()})
                    
                    if user_id not in session.keys():
                        session[user_id] = f"check-id-{user_id}"
                    
                    db_session.commit()
                    return UserResult.SUCCESS
                
            return UserResult.FAIL
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR


    def logout(self, db_session: Session, session: Dict[str, Any]) -> UserResult:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            session (Dict[str, Any]): 세션이 존재하는지 확인하기 위한 Session. \n
        
        Returns:
            UserResult.SUCCESS: 로그아웃 성공. (세션에 존재하지 않는다면, 로그아웃 성공으로 간주함)\n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """

        try:
            if self.user_id in session.keys():
                del session[self.user_id.__str__()]
                db_session.query(User).update({"logout_at": datetime.now()})
                db_session.commit()
                return UserResult.SUCCESS
            
            else:
                return UserResult.FAIL
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
    @staticmethod
    def forgot_password(db_session: Session, session:Dict[str, Any], user_id: str, new_password: str) -> UserResult:
        """
        Parameters:
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            user_id (str): 유저가 변경할 비밀번호의 아이디 \n
            session (Dict[str, Any]): 로그인을 관리하는 세션 \n
            new_password (str): 유저가 변경할 새로운 비밀번호 \n
        
        Returns:
            UserResult.SUCCESS: 비밀번호 변경 성공. \n
            UserResult.FAIL: 비밀번호 변경 실패. \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """
        try:
            user = User._load_user_info(db_session, user_id = user_id)
            if not user:
                return UserResult.FAIL
            
            hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            db_session.query(User).filter_by(seq = user.seq).update({"password": hashed_password, "password_update_at": datetime.now()})
            db_session.commit()
            del session[user_id]
            return UserResult.SUCCESS
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
    
    def update_profile_image(self, db_session: Session, session: Dict[str, Any], profile: Optional[bytes]) -> UserResult:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            session (Dict[str, Any]): 세션이 존재하는지 확인하기 위한 Session. \n
            profile (Optional[bytes]): 프로필 이미지 파일. None은 기본 이미지로 변경. \n
        
        Returns:
            UserResult.SUCCESS: 프로필 이미지 변경 성공 \n
            UserResult.TIME_OUT: 세션 만료 \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러 \n
        """
        
        if not self._check_exsit_session(session):
            return UserResult.TIME_OUT
        
        try:
            if profile:
                file_name = f"{str(uuid.uuid4())}.jpg"
                with open(os.path.join("./images", file_name), "wb") as fp:
                    fp.write(profile)
                    
                self.profile = os.path.join("./images", file_name)
                
            else:
                self.profile = None

            db_session.query(User).update({"profile": self.profile})
            db_session.commit()
            return UserResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
            
    def load_saved_items(self, db_session: Session) -> List[int]:
        """
        Parameters:
            self: 클랙스 객체 본인. \n
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            
        Returns:
            True: 물품이 추가되어 있음. \n
            False: 물품이 추가되어 있지 않음. \n
        """
        try:
            saved_items = SavedItems.get_saved_items_by_user_seq(db_session, self.seq) # type: ignore
            return list(map(lambda x: x.info["item_seq"], saved_items))
            
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return []
    
    def update_saved_items(self, db_session: Session, item_seq: int) -> UserResult:
        """
        Parameters:
            self: 클랙스 객체 본인. \n
            db_session (Session): 데이터베이스 연동을 위한 sqlalchemy Session 객체. \n
            item_seq (int): 좋아하는 상품의 고유 번호. \n
            
        Returns:
            UserResult.SUCCESS: 성공적으로 변경 성공. \n
            UserResult.FAIL: 변경 실패. \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """
        try:
            items = self.load_saved_items(db_session)
            if item_seq not in items:
                saved_item = SavedItems(self.seq, item_seq, datetime.now()) #type: ignore
                db_session.add(saved_item)
                
            else:
                db_session.query(SavedItems).filter_by(user_seq = self.seq, item_seq = item_seq).delete()
                
            db_session.commit()
            return UserResult.SUCCESS

        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR