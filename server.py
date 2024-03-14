import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import uuid
import sys
import enum
from database import Database

import logging
#logging.getLogger('flask_cors').level = logging.INFO

class Status(enum.Enum):
    MATCH="match"
    MISMATCH="miss_match"
    USED="used"
    INVALID_WORD="invalid_word"
    INVALID_USER_ARG="invalid_user_argument"
    INVALID_WORD_ARG="invalid_word_argument"
    INVALID_WORD_FORMAT="invalid_word_format"
    MISS_ALL="miss_all"
    INVALID_USER_ID = "invalid_user_id"

USER_ID_ARG = "userid"
WORD_ARG = "word"
    
app = Flask(__name__)
CORS(app)
db = Database(logger=app.logger)

@app.route("/")
def index():
    return app.redirect("https://dimitrifrazao.github.io/wordle_front")

@app.route("/wordle/api", methods=['GET'])
def api():
    return jsonify({'api':'not setup yet'})

@app.route("/wordle/size", methods=['GET'])
def wordleSize():
    size = len(db.user_data)
    return jsonify({'size':size})

@app.route('/wordle', methods=['GET', 'POST'])
def wordle():
    if request.method == 'GET':
        app.logger.info("Wordle get")
        user_id = str(uuid.uuid4())
        app.logger.info(f"user id generated: {user_id}")
        word = db.getWord()
        app.logger.info(f"random word generated: {word}")
        if db.addUser(user_id=user_id, word=word) :
            app.logger.info("user added")
            return jsonify({'userid': user_id})
        return make_response(jsonify({'error':'user id already exists'}), 422)

    elif request.method == 'POST':
        app.logger.info("Word post")
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
            message = f"invalid user id: {user_id}" 
            app.logger.info(message)
            return_data = {'status':Status.INVALID_USER_ID.value, 'error':message}
            return make_response(jsonify(return_data), 422)

        word = str(request.args.get(WORD_ARG)).lower()
        if len(word) != 5 or word.isalpha() is False:
            message = f"invalid word: {word}"
            app.logger.info(message)
            return_data = {'status':Status.INVALID_WORD_FORMAT.value, 'error':message}
            return make_response(jsonify(return_data), 422)

        
        if db.hasWord(word=word) is False:
            app.logger.info(f"word does NOT exist: {word}")
            return jsonify({'status':Status.INVALID_WORD.value})

        data = db.getUserData(user_id=user_id)
        app.logger.info(data)
        user_word = data.pop()
        
        if word in data[1:]:
            app.logger.info("word already used")
            return jsonify({'status':Status.USED.value})

        turn = 1
        for index, guess in enumerate(data[1:]):
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
            app.logger.info("Match!")
            db.removeUser(user_id=user_id)
            return jsonify({'status':Status.MATCH.value, 'letter_colors': letter_colors, 'word':user_word})
        else:
            if turn == 6:
                app.logger.info("missed all guesses")
                db.removeUser(user_id=user_id)
                return jsonify({'status':Status.MISS_ALL.value, 'letter_colors': letter_colors, 'word':user_word, "missed":word})
            else:
                app.logger.info("missed word")
                return jsonify({'status':Status.MISMATCH.value, 'letter_colors': letter_colors, 'word':None})

if __name__ == '__main__':
    logging.basicConfig(filename='server.log', level=logging.INFO)

    port = 5000
    host='0.0.0.0'
    debug = False
    useSSL = True

    argv = sys.argv[1:]
    if '-skipssl' in argv:
        useSSL = False
    if '-debug' in argv:
        debug = True

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_path = os.path.join(dir_path, "ssl/private.key")
    cert_path = os.path.join(dir_path, "ssl/certificate.crt")
    context = (cert_path, key_path) if useSSL else None

    app.run(host=host, port=port, debug=debug, ssl_context=context)