import pymysql
from pymysql.constants import CLIENT
from .cfg.config import status
import logging
from hashlib import sha256, md5
from abc import abstractmethod

log = logging.getLogger("queries")


"""
    MySql database driver
    TODO: Farla diventare una classe astratta 
"""
class DB(object):
    """
        DB object
    """
    __table__ = ""

    def __init__(self) -> None:
        super().__init__() 

    def _db_open(self):
        try:
            conn = pymysql.connect(
                host=status.get("mode").MYSQL_DATABASE_HOST,
                user=status.get("mode").MYSQL_DATABASE_USER,
                password=status.get("mode").MYSQL_DATABASE_PASS,
                db=status.get("mode").MYSQL_DATABASE_DB,
                client_flag=CLIENT.MULTI_STATEMENTS
            )
            cur = conn.cursor()
            return conn, cur
        except Exception as db_connection_error:
            raise Exception(db_connection_error)

    def db_close(self):
        self.conn.close()

    @abstractmethod
    def init(self) -> None:
        pass
    
    @abstractmethod
    def _create_table(self) -> None:
        pass

class Login(DB):
    """
        Login Model
    """
    __table__ = "users"

    def __init__(self, monitor=True) -> None:
        super().__init__()
        self.usr = ""
        self.pwd = ""
        self.registered_users = None
        self.monitor = monitor
        self.conn, self.cur = self._db_open()
    
    def _hash_pass(self) -> str:
        """
            Return password hash
        """
        return sha256(self.pwd.encode()).hexdigest()

    def _are_valid_credentials(self):
        try:
            log.info("[VERIFY_CREDENTIALS]")
            sql = f'''
                SELECT username, password from {self.__table__} WHERE username=%s and password=%s
            '''
            self.cur.execute(sql, (self.usr, self._hash_pass()))
            row = self.cur.fetchone()
            if row:
                log.info("[VALID_CREDENTIALS]")
                return True
            else:
                log.warning("[INVALID_CREDENTIALS]")
                if self._is_monitor_active():
                    if not self.is_account_locked():
                        if self._are_max_attemps():
                            self._lock()
                            return False
                        else:
                            return "skip"
                    else:
                        return False
                else:
                    return "no_monitor"
        except Exception as check_user_error:
            log.error(f"[VERIFY_CREDENTIALS_ERROR]=>{check_user_error}")
            raise Exception(check_user_error)
    
    def _create_table(self) -> None:
        """
            Tables definition
        """
        try:
            log.info(f"[CREATING TABLE] : {self.__table__}, check_attempts")
            sql = f'''
                    CREATE TABLE IF NOT EXISTS {self.__table__} (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        username VARCHAR(20),
                        password VARCHAR(256),
                        isBlacklisted boolean default false
                    );
                    CREATE TABLE IF NOT EXISTS check_attempts (
                        username VARCHAR(20) NOT NULL,
                        attempts INT default 0,
                        UNIQUE(username, attempts)
                    );
                    INSERT INTO {self.__table__} (
                        username,
                        password,
                        isBlacklisted
                    ) SELECT * FROM (SELECT %s, %s, 0) as tmp
                    WHERE NOT EXISTS(
                        SELECT username from {self.__table__} WHERE username = %s
                    ) LIMIT 1;
                '''
            self.cur.execute(sql, (
                'Mike', 
                'a4b59a393b100ef4576cf90c6cb6e37e95fc3c7754d1563ecf2dfcbd29b2f973',
                'Mike')
            )
            self.conn.commit()
            log.info(sql)
            # init valid user attemps
            self.registered_users = self._get_all_registered_users()
            self._register_user()
        except Exception as tables_creation_error:
            log.error(f"[TABLE_ERROR]=>{tables_creation_error}")
            raise Exception(tables_creation_error)

    def _init_attempts(self):
        try:
            sql = '''
                INSERT INTO check_attempts(username)
                SELECT username FROM users WHERE NOT EXISTS (SELECT username FROM check_attempts)
            '''
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as init_attempts_error:
            log.error(f"[USERS_INIT_ATTEMPTS_ERROR]=> {init_attempts_error}")
            raise Exception(init_attempts_error)

    def _is_monitor_active(self):
        return self.monitor

    def _update_attempts(self) -> None:
        try:
            sql = '''
                UPDATE check_attempts
                SET attempts=attempts+1 WHERE username=%s
            '''
            self.cur.execute(sql, (self.usr))
            self.conn.commit()
            log.info(f"[ATTEMPS_UPDATED]=> User: {self.usr}")
        except Exception as attempts_error:
            log.info(f"[ATTEMPS_UPDATE_ERROR]=>{attempts_error}")   
            raise Exception(attempts_error)

    def _are_max_attemps(self) -> bool:
        try:
            sql = "SELECT attempts FROM check_attempts WHERE username=%s"
            self.cur.execute(sql, (self.usr))
            row = list(self.cur.fetchone())[0]
            log.info(f"[CURRENT_ATTEMPTS]=>User: {self.usr}-{row}")
            if row <=2:
                log.info("[UPDATING_ATTEMPS]")
                self._update_attempts()
                return False
            else:
                return True
        except Exception as max_attemps_check_error:
            log.error(f"[MAX_ATTEMPS_CHECK_ERROR]=> {max_attemps_check_error}")
            raise Exception(max_attemps_check_error)

    def _lock(self)-> None:
        try:
            sql = '''
                UPDATE users
                SET isBlacklisted=true
                WHERE username=%s
            '''
            self.cur.execute(sql, (self.usr))
            self.conn.commit()
            log.info(f"[ACCOUNT_LOCKED]=> User: {self.usr}")
        except Exception as account_lock_error:
            log.error(f"[ACCOUNT_LOCK_ERROR]=>{account_lock_error}")
            raise Exception(account_lock_error)

    def _get_all_registered_users(self):
        try:
            sql = f"SELECT username FROM {self.__table__}"
            self.cur.execute(sql)
            rows = self.cur.fetchall() #(<user>,)
            if rows:
                return [r[0] for r in rows]
            return None
        except Exception as get_users_error:
            raise Exception(get_users_error)

    def _register_user(self):    
        log.info(f"[REGISTERED_USERS_COUNT]=>{len(self.registered_users)}")
        for u in self.registered_users:
            log.info(f"[REGISTERING_VALID_USER]=> User: {u}")
            self._init_attempts()

    def is_account_locked(self):
        try:
            log.info("[CHECKING] ...")
            log.info(f"[VERIFY_IF_ACCOUNT_IS_LOCKED]=> User: {self.usr}")
            sql = f"SELECT isBlacklisted FROM {self.__table__} WHERE username=%s"
            self.cur.execute(sql, (self.usr))
            row = self.cur.fetchone()[0]
            if row == 1:
                log.info("[ACCOUNT_LOCKED]")
                return True
            log.info("[ACCOUNT_UNLOCKED]")
            return False
        except Exception as check_user_error:
            log.error(f"[CHECK_USER_ERROR]=>{check_user_error}")
            raise Exception(check_user_error)

    def is_valid_user(self):
        log.info(f"[CHECKING_IF_VALID_USER]=>User: {self.usr}")
        if self.usr in self.registered_users:
            log.info("[VALID_USER]")
            return True
        log.warning("[INVALID_USER]")
        return False

    def init(self) -> None:
        """
            Initialize model
        """
        self._create_table()

    def authenticate(self) -> str:
        """
            Authenticate users.
        """
        log.info(f"[AUTHENTICATION_CHECK]=>User: {self.usr}")
        account_status = ""
        if self.is_valid_user():
            valid = self._are_valid_credentials()
            if not valid:
                account_status = "locked_account"
            elif valid == "no_monitor" or valid == "skip":
                pass
            else:
                account_status = "valid_credentials"
                self._clear_attempts()
        else:
            account_status = "invalid_account"
        log.info("-"*30)
        return account_status

    def _clear_attempts(self):
        try:
            sql = '''
                UPDATE check_attempts
                SET attempts=0 WHERE username=%s
            '''
            if self._is_monitor_active():
            	self.cur.execute(sql, (self.usr))
            	self.conn.commit()
            	log.info(f"[ATTEMPS_CLEARED]=> User: {self.usr}")
        except Exception as attempts_error:
            log.info(f"[ATTEMPS_CLEAR_ERROR]=>{attempts_error}")   
            raise Exception(attempts_error)

    def stop_monitoring(self):
        pass

class Comment(DB):
    """
        Comment model
    """
    __table__ = "comments"

    def __init__(self) -> None:
        super().__init__()
        self.conn, self.cur = self._db_open()
        
    def _create_table(self) -> None:
        """
            Tables definition
        """
        try:
            log.info(f"[CREATING TABLE] : {self.__table__}")
            sql = f'''
                    CREATE TABLE IF NOT EXISTS {self.__table__} (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        comment VARCHAR(255)
                    )
                '''
            self.cur.execute(sql)
            log.info(sql)
        except Exception as tables_creation_error:
            raise Exception(tables_creation_error)

    def init(self) -> None:
        self._create_table()

    def add_comment(self, comment) -> None:
        """
            Add new comment
        """
        try:
            sql = "INSERT INTO `comments` (comment) VALUES (%s)"
            self.cur.execute(sql, (comment))
            self.conn.commit()
            log.info(f"[ADD_COMMENT]=>{comment}")
        except Exception as new_comment_error:
            raise Exception(new_comment_error)
    
    def get_all_comments(self):
        """
            Retrive all comments.
        """
        try:
            sql = f'''SELECT comment FROM {self.__table__}'''
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            log.info(sql)
            return rows
        except Exception as get_comments_error:
            raise Exception(get_comments_error)

    def search(self, comment):
        """
            Search for comments
            NOTE: Vulnerable entry point for attacker
        """
        try:
            # Re-enable security from code injection over here
            # sql = "SELECT `comment` FROM `comments` WHERE `comment` LIKE concat(%s,'%%')"
            # cur.execute(sql, (comment,))
            sql = f"SELECT `comment` FROM `{self.__table__}` WHERE `comment` LIKE '%{comment}%'"
            log.info(f"[SEARCH_COMMENTS]=>{sql}")
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except Exception as search_error:
            raise Exception(search_error)