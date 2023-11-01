from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Dict, Any

def load_mysql_user_info() -> Dict[str, Any]:
        try:
            f = open("user_info.txt", "r")

        except FileNotFoundError:
            raise FileNotFoundError("파일 경로가 잘못됐습니다.")

        lines = list(map(lambda x: x.replace("\n", ""), f.readlines()))
        keys, values = list(), list()

        for line in lines:
            split_line = list(map(lambda x: x.strip(), line.split("=")))
            if "" in split_line:
                raise ValueError("Please Enter Information on user_info.txt")

            keys.append(split_line[0])
            values.append(split_line[1])

        if len(keys) != len(values):
            raise IndexError("Please Match Keys And Values")

        must_info = ["host", "user", "password"]
        for info in must_info:
            if info not in keys:
                raise KeyError("Insufficient information entered")

        return {keys[i]: values[i] for i in range(len(keys))}
    
user_info = load_mysql_user_info()
DB_URL = f'mysql+pymysql://{user_info["user"]}:{user_info["password"]}@{user_info["host"]}:{user_info["port"]}/{user_info["db"]}'


class EngineConn(object):
    """ 데이터 베이스와 연동을 도와주는 클래스
    
    Methods:
        session_maker(self) : 데이터베이스와 연동 했을 때, 필요한 세션을 생성해 주는 class 메소드 \n
        connection(self): 데이터베이스와 연동을 해주는 class 메소드 \n
    """
    
    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴을 위해 추가"""
        if not hasattr(cls,'instance'):
            print("데이터베이스 연결에 성공하였습니다.")
            cls.instance = super(EngineConn, cls).__new__(cls)
            
        return cls.instance
    
    def __init__(self):
        self.engine = create_engine(DB_URL)
    
    def session_maker(self) -> Session:
        session = sessionmaker(bind = self.engine)
        return session()

    def connection(self) -> Connection:
        return self.engine.connect()
    