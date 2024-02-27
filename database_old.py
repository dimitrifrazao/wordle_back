import mysql.connector
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
        print("starting mysql connection")
        self.user = user
        self.password = password
        self.host = host
        self.database = database

    def connect(self):
        kwargs = {}
        if self.user: kwargs['user'] = self.user
        if self.password: kwargs['password'] = self.password
        if self.host: kwargs['host'] = self.host
        if self.database: kwargs['database'] = self.database
        self.conn = mysql.connector.connect(**kwargs)
        self.cursor = self.conn.cursor()

    @classmethod
    def createDefault(cls):
        return cls(user=cls.DEFAULT_USER, password=cls.DEFAULT_PASSWORD, host=cls.DEFAULT_HOST, database=cls.DATABASE_NAME)

    @classmethod
    def createDefaultNoDatabase(cls):
        return cls(user=cls.DEFAULT_USER, password=cls.DEFAULT_PASSWORD, host=cls.DEFAULT_HOST, database=None)

    def commit(self):
        self.conn.commit()

    def close(self):
        print("closing mysql connection")
        self.conn.close()

    def testConnections(self):
        assert self.getWord(), "failed to get word from database"
        assert self.addUser(user_id=self.TEST_USER_ID) is None, "failed to add user to database"
        assert self.hasUser(user_id=self.TEST_USER_ID), "failed to check user id"
        print("database test complete!")

    def databaseExists(self):
        sql_command = self.getCommandFromFile(file_name="database_exists.sql")
        self.cursor.execute(sql_command)
        return self.cursor.fetchone() != None

    def hasTables(self):
        sql_command = self.getCommandFromFile(file_name="count_tables.sql")
        self.cursor.execute(sql_command)
        data = self.cursor.fetchone()
        return int(data[0]) == 2

    def createDatabase(self):
        sql_command = self.getCommandFromFile(file_name="create_database.sql")
        self.cursor.execute(sql_command)
        print("database wordDB created")

    def createTables(self):
        sql_command = self.getCommandFromFile(file_name="create_wordlist_table.sql")
        self.cursor.execute(sql_command)
        sql_command = self.getCommandFromFile(file_name="create_game_table.sql")
        self.cursor.execute(sql_command)
        print("tables created")

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
        self.cursor.execute(sql_command)
        self.commit()

    def hasWord(self, word:str):
        sql_command = self.getCommandFromFile(file_name="has_word.sql")
        sql_command = sql_command.replace("word_str", word)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def getWord(self):
        sql_command = self.getCommandFromFile(file_name="fetch_word.sql")
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def getAllWords(self):
        sql_command = self.getCommandFromFile(file_name="get_all_words.sql")
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def addUser(self, user_id: str):
        sql_command = self.getCommandFromFile(file_name="add_user.sql")
        sql_command = sql_command.replace("user_id", user_id)
        self.cursor.execute(sql_command)
        self.commit()

    def hasUser(self, user_id: str):
        sql_command = self.getCommandFromFile(file_name="has_user.sql")
        sql_command = sql_command.replace("user_id", user_id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def setUserData(self, user_id:str, word:str, index_str: str):
        index = int(index_str)
        assert 6 > index >= 0, "index out of bound"
        assert len(word)==5, "word len is not 5"
        guess = list(DataBase.GuessEnum)[index].name
        sql_command = self.getCommandFromFile(file_name="set_user_data.sql")
        sql_command = sql_command.replace("user_id", user_id)
        sql_command = sql_command.replace("guess", guess)
        sql_command = sql_command.replace("word", word)
        self.cursor.execute(sql_command)
        self.commit()

    def getUserData(self, user_id:str) -> list:
        sql_command = self.getCommandFromFile(file_name="get_user_data.sql")
        sql_command = sql_command.replace("user_id", user_id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def setUserWord(self, user_id, word):
        sql_command = self.getCommandFromFile(file_name="set_user_word.sql")
        sql_command = sql_command.replace("user_id", user_id)
        sql_command = sql_command.replace("word_str", word)
        self.cursor.execute(sql_command)
        self.commit()

    def getUserWord(self, user_id):
        sql_command = self.getCommandFromFile(file_name="get_user_word.sql")
        sql_command = sql_command.replace("user_id", user_id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def getCommandFromFile(self, file_name: str):
        file_path = os.path.join(dir_path, "sql", file_name)
        assert os.path.exists(file_path), f"sql file not found: {file_path}"
        fd = open(file_path, 'r')
        sql_file = fd.read()
        fd.close()
        return sql_file