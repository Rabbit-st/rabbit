from config import MysqlConfig as mysqlcfg
import pymysql

class DB(object):
    @staticmethod
    def init_db():
        return pymysql.Connection(
                host=mysqlcfg.DB_HOST,
                port=int(mysqlcfg.DB_PORT),
                user=mysqlcfg.DB_USER,
                password=mysqlcfg.DB_PASSWORD,
                database=mysqlcfg.DB_DATABASE,
                charset=mysqlcfg.DB_CHARSET)

    @staticmethod
    def get_cursor(conn):
        try:
            conn.ping(reconnect=True, attempts=3, delay=5) # 重连
        except Exception as e:
            conn = DB.init_db()
        return conn.cursor()
