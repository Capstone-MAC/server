from pymysql.connections import Connection
import traceback
import logging

class DBSettings:
    """ 데이터 베이스의 세팅(테이블 생성, 키 생성, 인덱스 생성)을 도와주는 클래스
    
    Methods:
        check_exist_table (conn, table): 생성하려고 하는 테이블과 같은 이름의 테이블이 존재하는지 확인하는 static 메소드
        create_user_table (conn): 유저 테이블 생성
    """
    
    @staticmethod
    def check_exist_table(conn: Connection, table: str) -> bool:
        cursor = conn.cursor()
        result = cursor.execute(f"SHOW TABLES LIKE '{table}';")
        cursor.close()

        return result != 0
    
    @staticmethod
    def create_user_table(conn: Connection) -> bool:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE `user` (
                    `seq`	BIGINT UNSIGNED AUTO_INCREMENT,
                    `address_Seq`	VARCHAR(255)	NOT NULL,
                    `user_id`	VARCHAR(15)	NOT NULL UNIQUE,
                    `password`	VARCHAR(60)	NOT NULL	COMMENT 'bcrypt를 통해 암호화',
                    `name`	VARCHAR(6)	NOT NULL,
                    `phone`	VARCHAR(11)	NOT NULL,
                    `email`	TEXT	NOT NULL,
                    `profile`	TEXT	NULL	DEFAULT NULL,
                    `idnum`	VARCHAR(13)	NOT NULL,
                    `signup_date`	DATETIME	NOT NULL,
                    `password_update_date`	DATETIME	NOT NULL,
                    `last_login`	DATETIME	NOT NULL,
                    `saved_items`	TEXT	NULL	DEFAULT ("[]"),
                    `saved_categories`	TEXT	NULL	DEFAULT ("[]"),
                    PRIMARY KEY (`seq`),
                    INDEX (`seq`)
                );
            """)
            
            return cursor.rowcount > 0
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return False
            
        finally:
            cursor.close()
    