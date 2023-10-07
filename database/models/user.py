from typing import List, Optional, TypeVar, Dict, Any
from pymysql.connections import Connection
from pydantic import BaseModel
from enum import Enum
import traceback
import datetime
import logging
import bcrypt
import uuid
import os

User = TypeVar("User", bound="User")


class UserResult(Enum):
    """ 유저가 어떤 행동을 할 때, 결과를 클래스로 구현

    Parameters:
        SUCCESS: 성공 \n
        FAIL: 실패 \n
        FORBIDDEN: 금지됨 \n
        NOTFOUND: 찾을 수 없음 \n
        TIME_OUT: 세션 만료됨 \n
        CONFLICT: 데이터 충돌됨 \n
        INTERNAL_SERVER_ERROR: 서버 내부 에러 \n
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
    
    
class SignoutModel(BaseModel):
    """ 유저가 회원탈퇴를 할 때, 보안을 위해 사용되는 클래스
    
    """
    user_id: str
    password: str


class LoginModel(BaseModel):
    """ 유저가 로그인을 할 때, 보안을 위해 사용되는 클래스
    
    """
    user_id: str
    password: str
    
class ForgotPasswordModel(BaseModel):
    """ 유저가 비밀번호를 변경 할 떄, 보안을 위해 사용되는 클래스
    
    """
    user_id: str
    new_password: str


class User:
    """ User class
    
    Methods:
        _load_user_info (conn: Connection, seq: Optional[int] = None, user_id: Optional[str] = None, email: Optional[str] = None): 유저 식별 정보를 통해 유저 정보를 데이터베이스 에서 불러오는 static 메소드 \n
        _check_exsit_session(self, session: Dict[str, Any]): 유저의 로그인이 유효한지 세션을 검사하는 class 메소드 \n
        info(self): 사용자의 정보를 조회하는 class 메소드 \n
        check_duplicate(conn: Connection, user_id: Optional[str] = None, email: Optional[str] = None): 데이터 중복을 확인하기 위해 사용되는 static 메소드, 아이디와 이메일만 제공 \n
        signup(conn: Connection, user_id: str, password: str, name: str, email: str, phone: str, idnum: str, address_seq: int): 회원가입 할 때 사용되는 static 메소드 \n
        signout(self, conn: Connection, session: Dict[str, Any]): 회원탈퇴 할 때 사용되는 class 메소드 \n
        login(conn: Connection, session: Dict[str, Any], user_id: str, password: str): 로그인 할 때 사용되는 static 메소드 \n
        logout(self, conn: Connection, session: Dict[str, Any]): 로그아웃 할 때 사용되는 class 메소드 \n
        forgot_password(conn:Connection, user_id: str, new_password: str): 사용자가 비밀번호를 잃어버렸을 때 사용되는 static 메소드 \n
        update_profile_image(self, conn: Connection, session: Dict[str, Any], profile: Optional[bytes]): 사용자의 프로필 이미지를 업데이트 할 때 사용되는 class 메소드 \n
    """
    seq: int # 유저 일련번호
    user_id: str # 유저 아이디
    password: str # 유저 비밀번호
    name: str # 유저 이름
    email: str # 유저 이메일
    phone: str # 유저 핸드폰 번호
    profile: str # 유저 프로필 이미지 경로
    idnum: str # 주민등록번호
    address_seq: int # 유저 주소 고유 번호
    signup_date: datetime.datetime # 회원가입 날짜
    password_update_date: datetime.datetime # 비밀번호 업데이트 날짜
    last_login: datetime.datetime # 마지막 로그인 날짜
    saved_items: List[int] # 찜한 물건들
    saved_categories: List[int] # 찜한 카테고리
    
    def __init__(self, seq: int, user_id: str, password: str, name: str, email: str, phone: str, profile: str, idnum: str, address_seq: int, signup_date: datetime.datetime, password_update_date: datetime.datetime, last_login: datetime.datetime, saved_items: List[int], saved_categories: List[int]) -> None:
        self.seq = seq
        self.user_id = user_id
        self.password = password
        self.name = name
        self.email = email
        self.phone = phone
        self.profile = profile
        self.idnum = idnum
        self.address_seq = address_seq
        self.signup_date = signup_date
        self.password_update_date = password_update_date
        self.last_login = last_login
        self.saved_items = saved_items
        self.saved_categories = saved_categories
        
        
    @staticmethod
    def _load_user_info(conn: Connection, seq: Optional[int] = None, user_id: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        """
        Parameters
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
            seq (int | None): 사용자 고유 번호를 통해 정보를 불러옴 \n
            user_id (str | None): 사용자 아이디를 통해 정보를 불러옴 \n
            email (str | None): 사용자 이메일을 통해 정보를 불러옴 \n
            
        Returns:
            User: 사용자 정보를 담은 User 객체 \n
            None: 정보를 불러오는데 실패 \n
        """
        cursor = conn.cursor()
        try:
            op = ""
            if not seq and not user_id and not email:
                return None
            
            if seq:
                op += f"seq={seq}"
                
            if user_id:
                op += f"user_id='{user_id}'"
                
            if email:
                op += f"email='{email}'"
                
            cursor.execute(f"SELECT * FROM user WHERE {op};")
            
            results = cursor.fetchall()
            return User(*results[0])
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return None

        finally:
            cursor.close()
            

    def _check_exsit_session(self, session: Dict[str, Any]) -> bool:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            session (Dict[str, Any]): 유저 로그인을 제어하기 위한 Session \n
            
        Returns:
            True: 세션에 아이디가 존재 \n
            False: 세션에 아이디가 존재하지 않음 \n
        """

        try:
            return self.user_id in session.keys()
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return False

    def info(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "idnum": self.idnum,
            "profile": self.profile,
            "address": "아직 미제공",
            "signup_date": self.signup_date,
            "password_update_date": self.password_update_date,
            "last_login": self.last_login,
            "saved_items": "아직 미제공",
            "saved_categories": "아직 미제공"
        }
        
    @staticmethod
    def check_duplicate(conn: Connection, user_id: Optional[str] = None, email: Optional[str] = None) -> UserResult:
        """
        Parameters:
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
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

            return UserResult.SUCCESS if cursor.rowcount == 0 else UserResult.CONFLICT

        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()
            
    
    @staticmethod
    def signup(conn: Connection, user_id: str, password: str, name: str, email: str, phone: str, idnum: str, address_seq: int) -> UserResult:
        """
        Parameters:
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
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
            
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(f"""
                INSERT INTO user(user_id, password, name, email, phone, idnum, address_seq, signup_date, password_update_date, last_login) 
                VALUES ('{user_id}', '{hashed_password}', '{name}', '{email}', '{phone}', '{idnum}', {address_seq}, '{signup_date}', '{password_update_date}', '{last_login}');
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
            
    
    def signout(self, conn: Connection, session: Dict[str, Any]) -> UserResult:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
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
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                DELETE FROM user WHERE seq={self.seq};            
            """)
            
            if cursor.rowcount > 0:
                conn.commit()
                return UserResult.SUCCESS
            
            else:
                return UserResult.FAIL
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()
    
        
    @staticmethod
    def login(conn: Connection, session: Dict[str, Any], user_id: str, password: str) -> UserResult:
        """
        Parameters:
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
            session (Dict[str, Any]): 유저 로그인을 제어하기 위한 Session \n
            user_id (str): 유저가 로그인 할 때 사요하는 아이디. \n
            password (str): 유저가 로그인 할 떄 사용하는 비밀번호, 클라이언트에서 암호화 하여 전송. \n
            
        Returns:
            UserResult.SUCCESS: 로그인 성공. \n
            UserResult.FAIL: 로그인 실패. \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """
        
        cursor = conn.cursor()
        try:
            user_info = User._load_user_info(conn, user_id = user_id)
            if user_info:
                if bcrypt.checkpw(password.encode("utf-8"), user_info.password.encode("utf-8")):
                    cursor.execute(f"""
                        UPDATE user
                        SET last_login = '{datetime.datetime.now()}'
                        WHERE seq={user_info.seq};            
                    """)
                    if user_id not in session.keys():
                        session[user_info.user_id] = f"check-id-{user_id}"
                    
                    conn.commit()
                    return UserResult.SUCCESS
                
            return UserResult.FAIL
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()


    def logout(self, conn: Connection, session: Dict[str, Any]) -> UserResult:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
            session (Dict[str, Any]): 세션이 존재하는지 확인하기 위한 Session. \n
        
        Returns:
            UserResult.SUCCESS: 로그아웃 성공. (세션에 존재하지 않는다면, 로그아웃 성공으로 간주함)\n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """
        
        cursor = conn.cursor()
        try:
            if self.user_id in session.keys():
                del session[self.user_id]
                cursor.execute(f"""
                        UPDATE user
                        SET last_login = '{datetime.datetime.now()}'
                        WHERE seq={self.seq};            
                    """)
                conn.commit()
            
            return UserResult.SUCCESS
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()
        
    @staticmethod
    def forgot_password(conn:Connection, user_id: str, new_password: str) -> UserResult:
        """
        Parameters:
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
            user_id (str): 유저 비밀번호 찾기를 위해 유저 아이디를 통해 정보 조회. \n
            new_password (str): 변경할 새로운 비밀번호. \n
            
        Returns:
            UserResult.SUCCESS: 비밀번호 변경 성공. \n
            UserResult.FAIL: 비밀번호 변경 실패. \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러. \n
        """
        
        cursor = conn.cursor()
        try:
            user = User._load_user_info(conn, user_id = user_id)
            if not user:
                return UserResult.FAIL
            
            new_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            cursor.execute(f"""
                UPDATE user
                SET password='{new_password}', password_update_date='{datetime.datetime.now()}'
                WHERE seq={user.seq};
            """)
            
            if cursor.rowcount > 0:
                conn.commit()
                return UserResult.SUCCESS
            
            else:
                return UserResult.FAIL
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()
            
    
    def update_profile_image(self, conn: Connection, session: Dict[str, Any], profile: Optional[bytes]) -> UserResult:
        """
        Parameters:
            self: 클래스 객체 본인. \n
            conn (Connection): 데이터베이스 연동을 위한 pymysql Connection 객체. \n
            session (Dict[str, Any]): 세션이 존재하는지 확인하기 위한 Session. \n
            profile (Optional[bytes]): 프로필 이미지 파일. None은 기본 이미지로 변경. \n
        
        Returns:
            UserResult.SUCCESS: 프로필 이미지 변경 성공 \n
            UserResult.FAIL: 프로필 이미지 변경 실패(기존과 같은 이미지) \n
            UserResult.TIME_OUT: 세션 만료 \n
            UserResult.INTERNAL_SERVER_ERROR: 서버 내부 에러 \n
        """
        
        if not self._check_exsit_session(session):
            return UserResult.TIME_OUT
        
        cursor = conn.cursor()
        try:
            if profile:
                file_name = f"{str(uuid.uuid4())}.jpg"
                with open(os.path.join("./images", file_name), "wb") as fp:
                    fp.write(profile)
                
                cursor.execute(f"""
                    UPDATE user
                    SET profile = './images/{file_name}'
                    WHERE user_id='{self.user_id}';
                """)
            
            else:
                cursor.execute(f"""
                    UPDATE user
                    SET profile = NULL
                    WHERE user_id='{self.user_id}'            
                """)
            
            if cursor.rowcount > 0:
                conn.commit()
                return UserResult.SUCCESS
                
            else:
                return UserResult.FAIL
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return UserResult.INTERNAL_SERVER_ERROR
        
        finally:
            cursor.close()
    