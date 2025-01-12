from flask import Flask, request, jsonify
from services.general import (
    login,
    create_question_and_answers,
    get_quiz_info,
    get_question_by_int,
    update_question,
    delete_all_questions,
    delete_all_scores,
    create_participation,
    delete_one_question,
    rebuild,
)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return f"Hello world !"


@app.route('/rebuild-db', methods=['POST'])
def rebuild_database():
    auth_token = request.headers.get('Authorization')
    response, status_code = rebuild(auth_token)
    return response, status_code


# public
# GET
@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
    response, status_code = get_quiz_info()
    return jsonify(response), status_code


@app.route('/questions/<int:questionId>', methods=['GET'])
def GetQuestionByID(questionId):
    response, status_code = get_question_by_int(questionId, 'question_id')
    return jsonify(response), status_code


@app.route('/questions', methods=['GET'])
def GetQuestionByPosition():
    position = request.args.get('position', type=int)
    response, status_code = get_question_by_int(position, 'position')
    return jsonify(response), status_code


# POST
@app.route('/participations', methods=['POST'])
def PostAnswers():
    payload = request.get_json()
    response, status_code = create_participation(payload)
    return jsonify(response), status_code


@app.route('/login', methods=['POST'])
def PostLogin():
    payload = request.get_json()
    response, status_code = login(payload)
    return jsonify(response), status_code


# privates
# POST
@app.route('/questions', methods=['POST'])
def PostQuestion():
    auth_token = request.headers.get('Authorization')
    payload = request.get_json()

    response, status_code = create_question_and_answers(payload, auth_token)

    return jsonify(response), status_code


# PUT
@app.route('/questions/<int:questionPos>', methods=['PUT'])
def PutQuestion(questionPos):
    auth_token = request.headers.get('Authorization')
    payload = request.get_json()
    response, status_code = update_question(questionPos, payload, auth_token)
    return response, status_code


# DELETE
@app.route('/questions/<int:questionId>', methods=['DELETE'])
def DeleteQuestion(questionId):
    auth_token = request.headers.get('Authorization')
    response, status_code = delete_one_question(questionId, auth_token)
    return response, status_code


@app.route('/questions/all', methods=['DELETE'])
def DeleteQuestions():
    auth_token = request.headers.get('Authorization')
    response, status_code = delete_all_questions(auth_token)
    return response, status_code


@app.route('/participations/all', methods=['DELETE'])
def DeleteParticipations():
    auth_token = request.headers.get('Authorization')
    response, status_code = delete_all_scores(auth_token)
    return response, status_code


if __name__ == "__main__":
    app.run(debug=True)
