from flask import Flask, request, send_from_directory, json, jsonify
from flask.wrappers import Response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS, cross_origin
import uuid
import database as database
import sys
import enum
import logging
from server_data import ServerData

logging.getLogger('flask_cors').level = logging.DEBUG


app = Flask(__name__)
CORS(app)
db: database.DataBase = database.DataBase.createDefault()

class Status(enum.Enum):
    MATCH="match"
    MISMATCH="miss_match"
    USED="used"
    INVALID_WORD="invalid_word"
    INVALID_USER_ARG="invalid_user_argument"
    INVALID_WORD_ARG="invalid_word_argument"
    MISS_ALL="miss_all"

class Wordle(Resource):
    """
    Wordle resource
    """
    USER_ID_ARG = "userid"
    WORD_ARG = "word"
    
    def post(self):
        print("Word get")
        if(Wordle.USER_ID_ARG not in request.args):
            message = f'{Wordle.USER_ID_ARG} argument not found'
            return json.dumps({'status':Status.INVALID_USER_ARG.value, 'error':message}), 422, {'ContentType':'application/json'} 
        if(Wordle.WORD_ARG not in request.args):
            message = f'{Wordle.WORD_ARG} argument not found'
            return json.dumps({'status':Status.INVALID_WORD_ARG.value, 'error':message}), 422, {'ContentType':'application/json'} 

        user_id = str(request.args.get(Wordle.USER_ID_ARG))
        word = str(request.args.get(Wordle.WORD_ARG))
        letter_colors = '     '
        word_exists = db.hasWord(word=word)

        if word_exists is False:
            print("word does NOT exist: " + word)
            return json.dumps({'status':Status.INVALID_WORD.value}), 200, {'ContentType':'application/json'} 

        data = db.getUserData(user_id=user_id)
        print(data)
        user_word = data[-1]
        
        if word in data[1:7]:
            print("word already used")
            return json.dumps({'status':Status.USED.value}), 200, {'ContentType':'application/json'} 

        turn = 0
        for index, guess in enumerate(data[1:7]):
            turn = index + 1
            if guess is None:
                db.setUserData(user_id=user_id, word=word, index_str=str(index)) 
                break
        
        stack = [' '] * 5
        for i in range(5):
            if word[i] == user_word[i]: # green 
                stack[i] = 'g'
            elif word[i] in user_word: # yellow
                stack[i] = 'y'
        letter_colors = "".join(stack)

        if word == user_word:
            print("Match!")
            return json.dumps({'status':Status.MATCH.value, 'letter_colors': letter_colors, 'word':user_word}), 200, {'ContentType':'application/json'} 
        else:
            print("word exists")
            if turn == 6:
                print("missed all guesses")
                return json.dumps({'status':Status.MISS_ALL.value, 'letter_colors': letter_colors, 'word':user_word}), 200, {'ContentType':'application/json'} 
            else:
                print("missed word")
                return json.dumps({'status':Status.MISMATCH.value, 'letter_colors': letter_colors, 'word':None}), 200, {'ContentType':'application/json'} 

    #@cross_origin(supports_credentials=True)    
    #@app.route('/wordle/get-user', methods=['POST'])
    def get(self):
        
        #db.lockTable()
        print("Wordle post")
        print(request.headers)
        user_id = str(uuid.uuid4())
        print("user id generated: ", user_id)
        db.addUser(user_id=user_id) 
        #db.unlockTables()
        print("user added")
        word = db.getWord()[0]
        print("random word generated: ", word)
        db.setUserWord(user_id=user_id, word=word)
        print("word set to user")
        response = jsonify({'userid': user_id})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
api = Api(app)
api.add_resource(Wordle, '/wordle')

@app.route("/")
def index():
    return send_from_directory("static/dist", "index.html")

if __name__ == '__main__':
    argv = sys.argv[1:]
    ip = 'localhost'
    port = 5000
    kwargs = {}
    if len(argv) > 0:
        kwargs['user'] =argv[0]
    if len(argv) > 1:
        kwargs['password'] = argv[1]
    if len(argv) > 2:
        kwargs['host'] =argv[2]
    if len(argv) > 3:
        assert len(argv) == 5, "must enter ip and port"
        ip = argv[3]
        port = int(argv[4])

    if kwargs:
        kwargs['database'] = 'wordDB'
        db = database.DataBase(**kwargs)
    #db.connect()

    ServerData.createFile(ip, str(port))
    if port == 5000:
        app.run(debug=True, port=port)
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
    db.close()