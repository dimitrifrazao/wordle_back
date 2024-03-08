import random
import logging
from typing import List, Dict, Set

class UserData():

    def __init__(self, user_id:str, word:str):
        self.user_id:str = user_id
        self.word:str = word
        self.guesses:List[str | None] = [None] * 6
        
    def getData(self)->List[str | None]:
        return [self.user_id] + self.guesses + [self.word]

class Database:

    def __init__(self, logger:logging.Logger) -> None:
        with open('word_list.txt', 'r') as file:
            data:List[str] = file.readlines()
        self.words:List[str] = [d.rstrip() for d in data]
        self.words_set:Set[str] = set(self.words)
        self.user_data: Dict[str,UserData] = {}
        self.logger=logger

    def isUserIdValid(self, user_id:str)->bool:
        return user_id in self.user_data

    def getWord(self)->str:
        return self.words[random.randint(0, len(self.words)-1)]
    
    def hasWord(self, word:str)->bool:
        return word in self.words_set
    
    def getUserData(self, user_id:str)->List[str|None]:
        user_data:UserData = self.user_data[user_id]
        return user_data.getData()
    
    def setUserData(self, user_id:str, word:str, index:int)->bool:
        if user_id not in self.user_data:
            self.logger.info('user id not in the db')
            return False
        self.user_data[user_id].guesses[index] = word
        return True

    def addUser(self, user_id:str, word:str):
        if user_id in self.user_data:
            self.logger.info('user id already in the db')
            return False
        self.user_data[user_id] = UserData(user_id, word)
        return True

    def removeUser(self, user_id:str):
        self.logger.info(f'removing user id: {user_id}' )
        self.user_data.pop(user_id, None)

    
