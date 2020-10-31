import sqlite3
import os

class Database:
    def __init__(self, path=":memory:", isolation_level=None, **kwargs):
        path = os.path.realpath(path)
        self.connection = sqlite3.connect(path, isolation_level=isolation_level, **kwargs)
        self.cursor = self.connection.cursor()
        self.fetchall = self.cursor.fetchall
        self.fetchone = self.cursor.fetchone
        self.fetchmany = self.cursor.fetchmany
        self.close = self.connection.close
        self.execute = self.cursor.execute

    def create_table_if_not_exists(self, table:str, fields:dict):
        cmd = f"create table if not exists {table} ({', '.join([f'{k} {v}' for k,v in fields.items()])})"
        self.cursor.execute(cmd)
        return cmd

    def create_unique_index(self, table:str, id:str, field:str):
        cmd = f"create unique index {id} on {table} ({field})"
        self.cursor.execute(cmd)
        return cmd

    def create_table(self, table:str, fields:dict):
        cmd = f"create table if not exists {table} ({', '.join([f'{k} {v}' for k,v in fields.items()])})"
        self.cursor.execute(cmd)
        return cmd

    @property
    def conn(self):
        return self.connection

    @property
    def c(self):
        return self.cursor

    @property
    def all(self):
        return self.cursor.fetchall()

    @property
    def one(self):
        return self.cursor.fetchone()

    def insert(self, table:str, row:tuple):
        """Insère un item."""
        cmd = f"insert into {table} values ("+','.join(["?"]*len(row))+")"
        self.cursor.execute(cmd, row)
        return cmd

    def replace(self, table:str, values:dict):
        """Remplace un item."""
        columns = tuple(values.keys())
        row = tuple(values.values())
        cmd = f"replace into {table}({','.join(columns)}) values {row}"
        print(cmd)
        self.cursor.execute(cmd, row)
        return cmd

    def update(self, table:str, values:dict, conditions:dict={}):
        """Remplace un item."""
        cmd = f"update {table} set "+", ".join([k+"=?" for k in values.keys()])
        if conditions:
            cmd += " where "+", ".join([k+"=?" for k in  conditions.keys()])
        row = tuple(values.values())+tuple(conditions.values())
        self.cursor.execute(cmd, row)
        return cmd

    def select(self, table:str, column:str="*", conditions:dict={}, orderby:str="", order:str="asc", limit:str="", offset:str="", like:str=""):
        """Sélectionne un item."""
        cmd = f"select {column} from {table}"
        if conditions:
            cmd += f" where {' and '.join([f'{k}=?' for k in conditions.keys()])}"
        if like:
            cmd += f" like {like}"
        if orderby:
            cmd += f" order by {orderby} {order}"
        if limit:
            cmd += f" limit {limit}"
        if offset:
            cmd += f" offset {offset}"
        self.cursor.execute(cmd, tuple(conditions.values()))
        return cmd

    def delete(self, table:str, conditions:dict={}, orderby:str="", order:str="asc", limit:str="", offset:str="", like:str=""):
        """Supprime un item."""
        cmd = f"delete from {table}"
        if conditions:
            cmd += f" where {' and '.join([f'{k}=?' for k in conditions.keys()])}"
        if like:
            cmd += f" like {like}"
        if orderby:
            cmd += f" order by {orderby} {order}"
        if limit:
            cmd += f" limit {limit}"
        if offset:
            cmd += f" offset {offset}"
        self.cursor.execute(cmd, tuple(conditions.values()))
        return cmd

    def drop_table(self, table:str, if_exists:bool=False):
        """Oublie toutes la mémoire."""
        cmd = "drop table"
        if if_exists:
            cmd += " if exists"
        cmd += f" {table}";
        self.cursor.execute(cmd)
        return cmd

    @property
    def tables(self):
        cmd = "select name from sqlite_master where type='table'"
        self.cursor.execute(cmd)
        return self.all

    def __getitem__(self, args):
        """Sélectionne un item."""
        if isinstance(args, list) or isinstance(args, tuple):
            self.select(*args)
        else:
            self.select(args)
        return self.cursor.fetchall()

    def __setitem__(self, *args):
        """Set an item in the table."""
        self.insert(*args)

    def __len__(self):
        """Taille de la table."""
        return len(self.tables)

    def __del__(self):
        """Ferme la base de donnée."""
        self.connection.close()
    

if __name__=="__main__":
    db = Database()
    db.create_table(table="machin",  fields={"datetime":"text", "author":"text", "request":"text", "response":"text"})
    db.create_table_if_not_exists(table="machin",  fields={"datetime":"text", "author":"text", "request":"text", "response":"text"})
    db.insert(table="machin", row=["today", "me", "slt", "tg"])
    db.insert(table="machin", row=["avant-hier", "moa", "wesh", "tg"])
    db.select(column="*", table="machin", conditions={"datetime":"today", "author":"me"}, orderby="request", order="desc")
    print(db["machin", "author"])
    db["machin"] = ["demain", "toa", "osef", "tu pues"]
    print(db.all)
    db.select("machin", "datetime")
    print(db.one)
    db.select("machin")
    print(db.fetchmany(2))
    # db.forget_table("machin")
    print(db.tables)
    print(len(db["machin"]))
    print(db.cursor.lastrowid)
    print(db.update("machin", {"request":"osef"}, {"author":"me"}))
    print(db["machin"])
    db.close()
