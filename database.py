from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, inspect, text
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import enum

dir_path = os.path.dirname(os.path.realpath(__file__))

class DataBase:
    TEST_USER_ID = 'ef42fcc1-5a28-484e-89af-98385403d4ac'
    DEFAULT_USER = 'root'
    DEFAULT_PASSWORD = ""
    DEFAULT_HOST = 'localhost'
    DATABASE_NAME = "wordDB"

    class GuessEnum(enum.IntEnum):
        firstGuess = 0
        secondGuess = 1
        thirdGuess = 2
        fourthGuess = 3
        fifthGuess = 4
        sixthGuess = 5

    def __init__(self, user:str = 'root', password: str ='', host:str = "localhost", database=None):
        
        database_uri = "mysql+mysqlconnector://{}:{}@{}/{}".format(user, password, host, database)
        self.engine = create_engine(database_uri)
        self.connection = self.engine.connect()

    @classmethod
    def createDefault(cls):
        return cls(user=cls.DEFAULT_USER, password=cls.DEFAULT_PASSWORD, host=cls.DEFAULT_HOST, database=cls.DATABASE_NAME)

    @classmethod
    def createDefaultNoDatabase(cls):
        return cls(user=cls.DEFAULT_USER, password=cls.DEFAULT_PASSWORD, host=cls.DEFAULT_HOST, database=None)

    def close(self):
        print("closing mysql connection")
        self.connection.close()

    def testConnections(self):
        assert self.getWord(), "failed to get word from database"
        assert self.addUser(user_id=self.TEST_USER_ID) is None, "failed to add user to database"
        assert self.hasUser(user_id=self.TEST_USER_ID), "failed to check user id"
        print("database test complete!")

    def databaseExists(self):
        sql_command = self.getCommandFromFile(file_name="database_exists.sql")
        result = self.connection.execute(text(sql_command))
        return result.fetchone() != None

    def hasTables(self):
        sql_command = self.getCommandFromFile(file_name="count_tables.sql")
        result = self.connection.execute(text(sql_command))
        data = result.fetchone()
        return int(data[0]) == 2

    def createDatabase(self):
        sql_command = self.getCommandFromFile(file_name="create_database.sql")
        self.connection.execute(text(sql_command))
        print("database wordDB created")

    def createTables(self):
        sql_command = self.getCommandFromFile(file_name="create_wordlist_table.sql")
        self.connection.execute(text(sql_command))
        sql_command = self.getCommandFromFile(file_name="create_game_table.sql")
        self.connection.execute(text(sql_command))
        print("tables created")

    def lockTable(self):
        sql_command = self.getCommandFromFile(file_name="lock_table.sql")
        self.connection.execute(text(sql_command))

    def unlockTables(self):
        sql_command = self.getCommandFromFile(file_name="unlock_tables.sql")
        self.connection.execute(text(sql_command))

    def addWordsFromFile(self, file_name: str):
        file_path = os.path.join(dir_path, "sql", file_name)
        assert os.path.exists(file_path), f"file not found: {file_path}"
        f = open(file_path, 'r')
        for line in f.readlines():
            self.addWord(word=line)
        f.close()
        print(f"words added to table from file: {file_path}")

    def addWord(self, word: str):
        sql_command = self.getCommandFromFile(file_name="add_word.sql")
        sql_command = sql_command.replace("word_str", word)
        self.connection.execute(text(sql_command))
        self.connection.commit()

    def hasWord(self, word:str):
        sql_command = self.getCommandFromFile(file_name="has_word.sql")
        sql_command = sql_command.replace("word_str", word)
        result = self.connection.execute(text(sql_command))
        return len(result.all()) > 0

    def getWord(self):
        sql_command = self.getCommandFromFile(file_name="fetch_word.sql")
        result = self.connection.execute(text(sql_command))
        return result.fetchone()

    def getAllWords(self):
        sql_command = self.getCommandFromFile(file_name="get_all_words.sql")
        result = self.connection.execute(text(sql_command))
        return result.fetchone()

    def addUser(self, user_id: str):
        sql_command = self.getCommandFromFile(file_name="add_user.sql")
        sql_command = sql_command.replace("user_id", user_id)
        self.connection.execute(text(sql_command))
        self.connection.commit()

    def hasUser(self, user_id: str):
        sql_command = self.getCommandFromFile(file_name="has_user.sql")
        sql_command = sql_command.replace("user_id", user_id)
        result = self.connection.execute(text(sql_command))
        return result.fetchone()

    def setUserData(self, user_id:str, word:str, index_str: str):
        index = int(index_str)
        assert 6 > index >= 0, "index out of bound"
        assert len(word)==5, "word len is not 5"
        guess = list(DataBase.GuessEnum)[index].name
        sql_command = self.getCommandFromFile(file_name="set_user_data.sql")
        sql_command = sql_command.replace("user_id", user_id)
        sql_command = sql_command.replace("guess", guess)
        sql_command = sql_command.replace("word", word)
        self.connection.execute(text(sql_command))
        self.connection.commit()

    def getUserData(self, user_id:str) -> list:
        sql_command = self.getCommandFromFile(file_name="get_user_data.sql")
        sql_command = sql_command.replace("user_id", user_id)
        result = self.connection.execute(text(sql_command))
        return result.fetchone()

    def setUserWord(self, user_id, word):
        sql_command = self.getCommandFromFile(file_name="set_user_word.sql")
        sql_command = sql_command.replace("user_id", user_id)
        sql_command = sql_command.replace("word_str", word)
        self.connection.execute(text(sql_command))
        self.connection.commit()

    def getUserWord(self, user_id):
        sql_command = self.getCommandFromFile(file_name="get_user_word.sql")
        sql_command = sql_command.replace("user_id", user_id)
        result = self.connection.execute(text(sql_command))
        return result.fetchone()

    def getCommandFromFile(self, file_name: str):
        file_path = os.path.join(dir_path, "sql", file_name)
        assert os.path.exists(file_path), f"sql file not found: {file_path}"
        fd = open(file_path, 'r')
        sql_file = fd.read()
        fd.close()
        return sql_file
