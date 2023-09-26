from typing import Dict
import traceback
import logging
import pymysql
import os

class DBConnector:
    """ 데이터 베이스와 연동을 도와주는 클래스
    
    Methods:
        load_mysql_user_info (): user_info.txt 파일에서 유저 정보를 가져오는 메소드 (주의사항: main.py와 같은 파일 경로에서 실행해야함) \n
        connection (): DB와 연동해서 pymysql.connections.Connection 객체를 반환하는 메소드 \n
    """
    
    @staticmethod
    def load_mysql_user_info() -> Dict[str, str]:
        try:
            print(os.getcwd())
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

    @staticmethod
    def connection() -> pymysql.connections.Connection:
        user_info = DBConnector.load_mysql_user_info()

        try:
            return pymysql.connect(
                **user_info
            )

        except pymysql.err.OperationalError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            raise Exception("Error occured")

        except TypeError as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            raise Exception("Error occured")
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            raise Exception("Error occured")