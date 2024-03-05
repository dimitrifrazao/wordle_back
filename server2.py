from flask import Flask, request, send_from_directory, json, jsonify, make_response
from flask_cors import CORS
import uuid
import sys
import enum
import logging
import json_database
from server_data import ServerData
logging.getLogger('flask_cors').level = logging.DEBUG

class Status(enum.Enum):
    MATCH="match"
    MISMATCH="miss_match"
    USED="used"
    INVALID_WORD="invalid_word"
    INVALID_USER_ARG="invalid_user_argument"
    INVALID_WORD_ARG="invalid_word_argument"
    MISS_ALL="miss_all"
    INVALID_USER_ID = "invalid_user_id"

USER_ID_ARG = "userid"
WORD_ARG = "word"

ip = '44.218.136.154' # aws ec2 elastic ip address
port = 5000
host='0.0.0.0'
debug = True
    
db = json_database.Database()
app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return send_from_directory("static/dist", "index.html")
    #render_template("static/dist/index.html", data=data)

@app.route('/wordle', methods=['GET', 'POST'])
def wordle():
    if request.method == 'GET':
        print("Wordle post")
        print(request.headers)
        user_id = str(uuid.uuid4())
        print("user id generated: ", user_id)
        word = db.getWord()
        print("random word generated: ", word)
        #db.setUserWord(user_id=user_id, word=word)
        db.addUser(user_id=user_id, word=word) 
        print("user added")
        response = jsonify({'userid': user_id})
        #response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    elif request.method == 'POST':
        print("Word get")
        if(USER_ID_ARG not in request.args):
            message = f'{USER_ID_ARG} argument not found'
            return_data = {'status':Status.INVALID_USER_ARG.value, 'error':message}
            return make_response(jsonify(return_data), 422)
        if(WORD_ARG not in request.args):
            message = f'{WORD_ARG} argument not found'
            return_data = {'status':Status.INVALID_WORD_ARG.value, 'error':message}
            return make_response(jsonify(return_data), 422)

        user_id = str(request.args.get(USER_ID_ARG))
        if db.isUserIdValid(user_id=user_id) is False:
            print("invalid user id" + user_id)
            message = "invalid user id"
            return_data = {'status':Status.INVALID_USER_ID.value, 'error':message}
            return make_response(jsonify(return_data), 422)

        word = str(request.args.get(WORD_ARG)).lower()
        letter_colors = '     '
        word_exists = db.hasWord(word=word)
        if word_exists is False:
            print("word does NOT exist: " + word)
            return jsonify({'status':Status.INVALID_WORD.value})

        data = db.getUserData(user_id=user_id)
        print(data)
        user_word = data[-1]
        
        if word in data[1:7]:
            print("word already used")
            return jsonify({'status':Status.USED.value})

        turn = 1
        for index, guess in enumerate(data[1:7]):
            if guess is None:
                db.setUserData(user_id=user_id, word=word, index=index) 
                break
            turn += 1
        
        stack = [' '] * 5
        for i in range(5):
            if word[i] == user_word[i]: # green 
                stack[i] = 'g'
            elif word[i] in user_word: # yellow
                stack[i] = 'y'
        letter_colors = "".join(stack)

        if word == user_word:
            print("Match!")
            db.removeUser(user_id=user_id)
            return jsonify({'status':Status.MATCH.value, 'letter_colors': letter_colors, 'word':user_word})
        else:
            if turn == 6:
                print("missed all guesses")
                db.removeUser(user_id=user_id)
                return jsonify({'status':Status.MISS_ALL.value, 'letter_colors': letter_colors, 'word':user_word, "missed":word})
            else:
                print("missed word")
                return jsonify({'status':Status.MISMATCH.value, 'letter_colors': letter_colors, 'word':None})
            


if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) > 0:
        ip = str(argv[0])
        port = int(argv[1])
    ServerData.createFile(str(ip), str(port))

    app.run(host=host, port=port, debug=debug)