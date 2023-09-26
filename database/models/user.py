from pymysql.connections import Connection
from typing import List, Optional, TypeVar
from pydantic import BaseModel
from enum import Enum
import traceback
import datetime
import logging

User = TypeVar("User", bound="User")


class UserResult(Enum):
    """ 유저가 어떤 행동을 할 때, 결과를 클래스로 구현

    """
    SUCCESS = 200
    FAIL = 401
    FORBIDDEN = 403
    NOTFOUND = 404
    TIME_OUT = 408
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    
        
class SignUpModel(BaseModel):
    """ 유저가 회원가입을 할 때, 보안을 위해 사용되는 클래스
    
    """
    user_id: str
    password: str
    name: str
    email: str
    phone: str
    idnum: str
    address_seq: int


class User:
    """ User class
    
    Methods:
        check_duplicate(user_id = None, email = None) : 데이터 중복을 확인하기 위해 사용되는 static 메소드, 아이디와 이메일만 제공 \n
        signup(user_id, password, name, email, phone, idnum, address) : 회원가입 할 때 사용되는 static 메소드 \n
        login(user_id, password) : 로그인 할 떄 사용되는 static 메소드 \n
    """
    seq: int # 유저 일련번호
    user_id: str # 유저 아이디
    password: str # 유저 비밀번호
    name: str # 유저 이름
    email: str # 유저 이메일
    phone: str # 유저 핸드폰 번호
    idnum: str # 주민등록번호
    profile: Optional[str] # 유저 프로필 이미지 경로
    address_seq: int # 유저 주소 고유 번호
    signup_date: datetime.datetime # 회원가입 날짜
    password_update_date: datetime.datetime # 비밀번호 업데이트 날짜
    last_login: datetime.datetime # 마지막 로그인 날짜
    save_items: List[int] # 찜한 물건들
    save_categories: List[int] # 찜한 카테고리
    
    def __init__(self, user_id: str, password: str, name: str, email: str, phone: str, idnum: str, address_seq: int, profile: Optional[str] = None) -> None:
        self.user_id = user_id
        self.password = password
        self.name = name
        self.email = email
        self.phone = phone
        self.idnum = idnum
        self.profile = profile
        self.address = address_seq
        self.signup_date = datetime.datetime.now()
        self.password_update_date = datetime.datetime.now()
        self.last_login = datetime.datetime.now()
        self.save_items = []
        self.save_categories = []
        
    
    # @staticmethod
    # def _load_user_info(conn: Connection, user_id: Optional[str] = None, email: Optional[str] = None) -> User:
    #     pass
        
        
    @staticmethod
    def check_duplicate(conn: Connection, user_id: Optional[str] = None, email: Optional[str] = None) -> UserResult:
        """
        Parameters:
            user_id (str | None): 유저가 회원가입 할 때 중복 체크 하는 아이디. \n
            email (str | None): 유저가 회원가입 할 때 중복 체크 하는 이메일. \n
            
        Returns:
            UserResult.SUCCESS: 아이디 또는 이메일 사용 가능! \n
            UserResult.CONFLICT: 아이디 또는 이메일이 중복 됨! \n
            UserResult.INTERNAL_SERVER_ERROR: 중복 체크 도중 서버 코드 에러 발생! (에러 문구 확인) \n
        """
        cursor = conn.cursor()
        try:
            op = f"user_id = '{user_id}'" if user_id != None else f"email = '{email}'"
            cursor.execute(f"""
                SELECT * FROM user WHERE {op};            
            """)

            return UserResult.SUCCESS if cursor.rowcount == 0 else UserResult.FAIL

        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()
            
    
    @staticmethod
    def signup(conn: Connection, user_id: str, password: str, name: str, email: str, phone: str, idnum: str, address_seq: int) -> UserResult:
        """
        Parameters:
            user_id (str): 유저가 회원가입 할 때 사용하는 아이디, 중복 체크를 먼저 한 후에 사용. \n
            password (str): 유저가 회원가입 할 때 사용하는 비밀번호, 클라이언트에서 암호화 하여 전송. \n
            name (str): 유저의 이름 (성을 포함한 3글자). \n
            email (str): 유저의 이메일. \n
            phone (str): 유저의 폰 (-를 제외한 문자열 (예시: 01033475079)). \n
            idnum (str): 유저의 주민등록 번호 (-를 제외한 문자열 (예시: 0211233214325)). \n
            address (str): 유저의 집 주소 (). \n 
            
        Returns:
            UserResult.SUCCESS: 회원가입에 성공! \n
            UserResult.FAIL: 회원가입에 실패! \n
            UserResult.INTERNAL_SERVER_ERROR: 회원가입하는데 서버 코드에 에러가 발생! (에러 문구 확인) \n

        """
        
        cursor = conn.cursor()
        try:
            signup_date = datetime.datetime.now()
            password_update_date = datetime.datetime.now()
            last_login = datetime.datetime.now()
            
            cursor.execute(f"""
                INSERT INTO user(user_id, password, name, email, phone, idnum, address_seq, signup_date, password_update_date, last_login, saved_items, saved_categories) 
                VALUES ('{user_id}', '{password}', '{name}', '{email}', '{phone}', '{idnum}', {address_seq}, '{signup_date}', '{password_update_date}', '{last_login}', '[]', '[]');
            """)
            
            if cursor.rowcount > 0:
                conn.commit()
                return UserResult.SUCCESS

            return UserResult.FAIL
            
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
            
        finally:
            cursor.close()
        
    
    # @staticmethod
    # def login(user_id: str, password: str) -> User:
        """
        Parameters:
            user_id (str): 유저가 로그인 할 때 사요하는 아이디. \n
            password (str): 유저가 로그인 할 떄 사용하는 비밀번호, 클라이언트에서 암호화 하여 전송. \n
        """
        
        pass
