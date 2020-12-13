import datetime
from decimal import Decimal
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import exc


__all__ = ["Database",
           "Connection",
           "create_mysql_db",
           "create_sqlite_db"]


class Database(object):
    def __init__(self, url):
        self._engine = create_engine(url)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self._engine.dispose()

    def create_connection(self):
        #https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=auto%20commit#sqlalchemy.engine.Connection.execution_options.params.autocommit
        #self._engine.connect().execution_options(autocommit=True)
        #self._engine.connect().execution_options(isolation_level="REPEATABLE READ")
        return Connection(self._engine.connect())


class Connection(object):
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self._conn.close()

    def execute(self, stmt, fetchall=False,
                json_serializable=False, **bindparams):
        cur = self._conn.execute(text(stmt), **bindparams)
        if cur.returns_rows:
            return self._handle_select_cursor(cur, fetchall, json_serializable)
        return cur.rowcount
    
    def query(self, stmt, fetchall=True,
              json_serializable=True, **bindparams):
        return self.execute(stmt, fetchall, json_serializable, **bindparams)

    def _handle_select_cursor(self, cur, fetchall, serializable):
        gen = self._row_gen(cur, serializable)
        if not fetchall:
            return gen
        return [*gen]

    def _row_gen(self, cur, serializable):
        columns = cur.keys()
        for row in cur:
            yield self._format_row(row, columns, serializable)

    def _format_row(self, row, cols, serializable):
        if serializable:
            return dict(zip(cols, map(self._serializable, row)))
        return dict(zip(cols, row))

    def _serializable(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
                
    @contextmanager
    def transaction(self):
        tran = self._conn.begin()
        try:
            yield tran
            tran.commit()
        except Exception as err:
            tran.rollback()
            raise err


def create_mysql_db(user, password, server, port=3306, dbname=None):
    drivers = ["mysqlconnector", "mysqldb", "pymysql"]
    url_partial = "{user}:{pw}@{server}:{port}".format(user=user,
                                                       pw=password,
                                                       server=server,
                                                       port=port)
    if dbname:
        url_partial += "/{}".format(dbname)
    try:
        return Database("mysql://{url}".format(url=url_partial))
    except ImportError:
        conn_str_partial = "mysql+{driver}://" + url_partial
        for driver in drivers:
            try:
                return Database(conn_str_partial.format(driver=driver))
            except (exc.NoSuchModuleError, ImportError):
                pass
        raise AttributeError("couldn't find a required driver: {}".format(drivers))

def create_sqlite_db(path=None):
##    ["sqlite+pysqlite", "sqlite+pysqlcipher"]
    drivers = ["pysqlite", "pysqlcipher"]
    path = path or ":memory:"
    try:
        return Database("sqlite:///{}".format(path))
    except ImportError:
        conn_str_partial = "sqlite+{driver}:///" + path
        for driver in drivers:
            try:
                return Database(conn_str_partial.format(driver=driver))
            except (exc.NoSuchModuleError, ImportError):
                pass
        raise AttributeError("couldn't find a required driver: {}".format(drivers))
