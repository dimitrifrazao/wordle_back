from flask import jsonify
import random

class Database:

    class UserData():

        def __init__(self, user_id, word):
            self.user_id = user_id
            self.guesses = [None] * 6
            self.word = word         

    def __init__(self) -> None:
        with open('combined_wordlist.txt', 'r') as file:
            data = file.readlines()
        self.words = [d.rstrip() for d in data][1:]
        self.words_set = set(self.words)
        self.user_data = {}

    def isUserIdValid(self, user_id):
        return user_id in self.user_data

    def getWord(self):
        return self.words[random.randint(0, len(self.words)-1)]
    
    def hasWord(self, word):
        return word in self.words_set
    
    def getUserData(self, user_id):
        return [self.user_data[user_id].user_id] + self.user_data[user_id].guesses + [self.user_data[user_id].word]
    
    def setUserData(self, user_id, word, index):
        self.user_data[user_id].guesses[index] = word

    def addUser(self, user_id, word):
        if user_id in self.user_data:
            print('user id already in the db')
        self.user_data[user_id] = Database.UserData(user_id, word)

    def removeUser(self, user_id):
        print('removing user id ' + str(user_id))
        self.user_data.pop(user_id, None)

    
