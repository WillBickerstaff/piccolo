import os
import sqlite3 as sqlite
from util import check_file, make_hash

class DB(object):
    LATEST_DB = 1.0

    SCHEMA = """ 
      CREATE TABLE IF NOT EXISTS readings(timestamp decimal PRIMARY KEY NOT NULL,
                                          reading int NOT NULL);
      CREATE TABLE IF NOT EXISTS sys(key tinytext PRIMARY KEY NOT NULL,
                                     val tinytext NOT NULL);
      CREATE TABLE IF NOT EXISTS user(id int AUTOINCREMENT NOT NULL PRIMARY KEY,
                                      username tinytext NOT NULL UNIQUE,
                                      passhash text NOT NULL,
                                      salt text NOT NULL,
                                      email text);
    """


    def __init__(self, **kwargs):
        self.db = 'templog.db' if 'db' not in kwargs else kwargs['db']
        dbstat = check_file(db)
        os.environ['PIMMS_DB'] = db
        if dbstat == 2: self.createdb(self.db)

    
    def cursor(self):
        sqlite.connect(self.db) as con:
        return con.cursor

    def createdb(self):
        with self.cursor as cur:
            cur.executescript(DB.SCHEMA)
        self.defaultData()

    def defaultData(self):
        self.addadmin()
        self.adddbver()

    def exists(self, table, col, val):
        with self.cursor as cur:
            exists = cur.execute("SELECT 1 from {tablename} WHERE {colname} "
                                 "is '{reqval}';".format(colname = col,
                                                         tablename=table,
                                                         reqval=val))
            return True if len(exists.fetchall()) > 0  else False
  
    def addadmin(self):
        if not self.exists('user', 'username', 'admin'):
            passhash, salt = make_hash('admin')
            with self.cursor as cur:
                cur.execute("INSERT INTO user(username, passhash, salt) "
                            "VALUES ({ph}, {salt});".format(ph = passhash,
                                                            salt = salt))
    
    def adddbver(self):
        exists = self.exists('sys', 'key', 'dbver'):
        qry = ""
        if exists:
            qry = "UPDATE sys SET dbver='{dbv}' "
                  "WHERE key='dbver';".format(dbv = DB.LATEST_DB)
        else:
            qry = "INSERT INTO sys(key, val) VALUES "
                  "('dbver', '{dbv}');".format(dbv=DB.LATEST_DB)

        with self.cursor as cur:
            cur.execute(qry)
