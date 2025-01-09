import sqlite3
import datetime
from .jwt_utils import decode_token
from quiz_api.model.question import Question
from quiz_api.model.answer import Answer
from quiz_api.model.score import Score
import hashlib
from .jwt_utils import build_token

# chemin par rapport à app.py
path = 'database.db'


def login(payload):
    password = payload['password'].encode('utf-8')
    hashed = hashlib.md5(password).hexdigest()
    if hashed == 'd8170650479293c12e0201e5fdf45f40':
        return {"token": build_token()}, 200
    return 'Unauthorized', 401


def rebuild(auth_token: str):
    if not auth_token:
        return 'Authorization token is missing', 401

    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        decode_token(auth_token)
        # Suppression des tables existantes si elles existent déjà (optionnel)
        cursor.execute("DROP TABLE IF EXISTS answers")
        cursor.execute("DROP TABLE IF EXISTS questions")
        cursor.execute("DROP TABLE IF EXISTS scores")

        # Création de la table "questions"
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            position INTEGER NOT NULL UNIQUE,
            image TEXT
        )
        """)

        # Création de la table "answers"
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            question_id INTEGER NOT NULL,
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            is_correct INTEGER COLLATE BINARY,
            FOREIGN KEY(question_id) REFERENCES questions(question_id)
        )
        """)

        # Création de la table "scores"
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL UNIQUE,
            score NUMERIC,
            date TEXT NOT NULL
        )
        """)

        # Sauvegarder les modifications et fermer la connexion
        conn.commit()

    except sqlite3.Error as e:
        # Si une erreur se produit, on l'affiche
        print(f"Erreur lors de l'exécution des requêtes SQL : {e}")

    finally:
        # Assurer la fermeture de la connexion, même en cas d'erreur
        if conn:
            conn.close()
    return 'Ok', 200


def create_question_and_answers(payload: dict, auth_token: str) -> tuple:
    """
    Creates a new question and its answers in the database after validating the JWT token.

    :param payload: dict containing the question and answers data.
    :param auth_token: The Authorization token.
    :return: tuple: A tuple containing the response and the HTTP status code.
    """
    db_connection = sqlite3.connect(path)

    # Vérifier que le token d'authentification est présent
    if not auth_token:
        return 'Authorization token is missing', 401

    try:
        # Valider le token
        decode_token(auth_token)

        question = Question.from_json({k: v for k, v in payload.items() if k != 'possibleAnswers'})

        # Convertir les réponses possibles en une liste d'objets Answer
        answers = [Answer.from_json(answer) for answer in payload['possibleAnswers']]

        # Connexion à la base de données
        cursor = db_connection.cursor()

        # Vérifier si la position est déjà prise
        check_position_query = 'SELECT COUNT(*) FROM questions WHERE position = ?'
        cursor.execute(check_position_query, (question.position,))
        position_taken = cursor.fetchone()[0] > 0

        # Si la position est déjà prise, incrémenter les positions des autres questions
        if position_taken:
            # Récupérer toutes les questions dont la position est supérieure ou égale à la position souhaitée
            select_query = 'SELECT question_id, position FROM questions WHERE position >= ? ORDER BY position DESC'
            cursor.execute(select_query, (question.position,))
            rows = cursor.fetchall()

            # Incrémenter la position de chaque ligne
            for row in rows:
                current_id, current_position = row
                new_position = current_position + 1

                # Mettre à jour la position de la question en remontant
                update_position_query = 'UPDATE questions SET position = ? WHERE question_id = ?'
                cursor.execute(update_position_query, (new_position, current_id))

            db_connection.commit()

        # Préparer la requête d'insertion pour la question
        insert_question_query = '''
            INSERT INTO questions (title, text, position, image)
            VALUES (?, ?, ?, ?)
        '''

        # Insérer la question dans la base de données
        cursor.execute(insert_question_query, (question.title, question.text, question.position, question.image))
        db_connection.commit()

        # Récupérer l'ID de la question insérée
        question_id = cursor.lastrowid

        # Préparer les requêtes d'insertion pour les réponses
        insert_answer_query = '''
            INSERT INTO answers (question_id, text, is_correct)
            VALUES (?, ?, ?)
        '''

        # Insérer chaque réponse dans la base de données
        for answer in answers:
            cursor.execute(insert_answer_query, (question_id, answer.text, answer.is_correct))

        # Valider la transaction pour les réponses
        db_connection.commit()

        # Fermer la connexion à la base de données
        db_connection.close()

        # Retourner le code 200 avec l'ID de la question ajoutée
        return {"id": question_id}, 200

    except Exception as e:
        # En cas d'erreur dans l'insertion ou d'autres erreurs, annuler la transaction avec rollback
        db_connection.rollback()  # Annuler toute modification dans la base de données
        db_connection.close()
        return f"An error occurred: {e}", 500


def get_quiz_info() -> tuple:
    db_connection = sqlite3.connect(path)

    try:
        cursor = db_connection.cursor()
        # Requête pour obtenir le nombre de questions
        tot_questions_query = '''
            SELECT COUNT(*) FROM questions
        '''
        cursor.execute(tot_questions_query)
        tot_questions = cursor.fetchone()[0]  # Récupérer le premier résultat (nombre de questions)

        # Requête pour obtenir tous les scores
        scores_query = '''
            SELECT player_name, score, date FROM scores
        '''
        cursor.execute(scores_query)
        scores_data = cursor.fetchall()  # Récupérer tous les résultats (liste de tuples)

        # Créer des instances de Score et les convertir en JSON
        scores_json = []
        for score_data in scores_data:
            # Créer une instance de Score pour chaque ligne de la base de données
            score = Score(playerName=score_data[0], score=score_data[1], date=score_data[2])
            scores_json.append(score.to_json())

        db_connection.commit()
        db_connection.close()

        return {"size": tot_questions, "scores": scores_json}, 200

    except Exception as e:
        db_connection.rollback()
        db_connection.close()
        return f"An error occurred: {e}", 500


def get_question_by_int(integer: int, method: str) -> tuple:

    db_connection = sqlite3.connect(path)

    try:
        cursor = db_connection.cursor()

        # Récupérer la question par son ID ou sa position
        query_question = f'SELECT * FROM questions WHERE {method} = ?'
        cursor.execute(query_question, (integer,))
        question = cursor.fetchone()

        if question:
            # Récupérer les réponses possibles pour la question
            query_answers = 'SELECT * FROM answers WHERE question_id = ?'
            cursor.execute(query_answers, (question[0],))
            answers = cursor.fetchall()

            # Construire la liste des réponses possibles
            possible_answers = [{"id": answer[1], "text": answer[2], "isCorrect": bool(answer[3])}for answer in answers]

            # Renvoyer les données sous forme JSON
            question_json = {
                "id": question[0],
                "title": question[1],
                "position": question[3],
                "text": question[2],
                "image": question[4],
                "possibleAnswers": possible_answers
            }

            db_connection.close()
            return question_json, 200
        else:
            db_connection.close()
            return {"message": "Question not found"}, 404

    except Exception as e:
        db_connection.rollback()
        db_connection.close()
        return {"message": f"An error occurred: {e}"}, 500


def update_question(current_position, payload, auth_token) -> tuple:
    if not auth_token:
        return 'Authorization token is missing', 401
    new_pos = payload['position']  # La nouvelle position
    question_pos = current_position  # L'ID de la question que l'on déplace

    db_connection = sqlite3.connect(path)
    try:
        decode_token(auth_token)

        cursor = db_connection.cursor()

        # On récupère l'id de la question à modifier
        cursor.execute('SELECT question_id FROM questions WHERE position = ?', (question_pos,))
        question = cursor.fetchone()

        if not question:
            return {'message': 'Question not found'}, 404

        question_id = question[0]

        # Crée un objet Question à partir des données (en excluant 'possibleAnswers')
        question = Question.from_json({k: v for k, v in payload.items() if k != 'possibleAnswers'})

        # Convertir les réponses possibles en une liste d'objets Answer
        answers = [Answer.from_json(answer) for answer in payload['possibleAnswers']]

        cursor.execute('SELECT answer_id FROM answers WHERE question_id = ?', (question_id,))
        existing_answer_ids = cursor.fetchall()
        answers_id_list = [row[0] for row in existing_answer_ids]

        # Vérification si la position est déjà occupée
        cursor.execute('SELECT COUNT(*) FROM questions WHERE position = ?', (new_pos,))
        position_taken = cursor.fetchone()[0] > 0

        if position_taken:
            # Temporarily set the position of the question to a negative value
            cursor.execute('UPDATE questions SET position = ? WHERE position = ?', (-question_pos, question_pos))
            db_connection.commit()

            # Déplacer toutes les questions pour libérer la position
            if new_pos < question_pos:  # Déplacement vers le haut
                select_query = '''
                    SELECT question_id, position FROM questions 
                    WHERE position >= ? AND position < ? 
                    ORDER BY position DESC
                '''
                cursor.execute(select_query, (new_pos, question_pos))
                rows = cursor.fetchall()

                # Incrémenter la position de chaque ligne
                for row in rows:
                    current_id, current_position = row
                    new_position = current_position + 1

                    # Mettre à jour la position de la question en remontant
                    update_position_query = 'UPDATE questions SET position = ? WHERE question_id = ?'
                    cursor.execute(update_position_query, (new_position, current_id))

            else:  # Déplacement vers le bas
                update_query = '''
                    UPDATE questions
                    SET position = position - 1
                    WHERE position <= ? AND position > ?
                '''
                cursor.execute(update_query, (new_pos, question_pos))

            db_connection.commit()

            # Rétablir la question déplacée à sa nouvelle position
            cursor.execute('UPDATE questions SET position = ? WHERE question_id = ?', (new_pos, question_id))
            db_connection.commit()

        else:
            # Si la position n'est pas occupée, on peut directement la modifier
            cursor.execute('UPDATE questions SET position = ? WHERE question_id = ?', (new_pos, question_id))
            db_connection.commit()

        # Mettre à jour la question avec les nouveaux détails
        cursor.execute('''
                    UPDATE questions
                    SET title = ?, text = ?, position = ?, image = ?
                    WHERE question_id = ?
                ''', (question.title, question.text, new_pos, question.image, question_id))

        # Mettre à jour les réponses existantes
        for i, answer in enumerate(answers):
            answer_id = answers_id_list[i]
            cursor.execute('''
                UPDATE answers
                SET text = ?, is_correct = ?
                WHERE question_id = ? AND answer_id = ?
            ''', (answer.text, answer.is_correct, question_id, answer_id))

        # Commit les changements dans la base de données
        db_connection.commit()

        db_connection.close()

        return {'message': 'Question and answers updated successfully'}, 204

    except Exception as e:
        db_connection.rollback()
        db_connection.close()
        return {'message': f'An error occurred: {e}'}, 500


def delete_all_questions(auth_token) -> tuple:
    if not auth_token:
        return 'Authorization token is missing', 401
    db_connection = sqlite3.connect(path)

    try:
        decode_token(auth_token)

        cursor = db_connection.cursor()

        # 1. Supprimer toutes les réponses associées aux questions
        cursor.execute('''
            DELETE FROM answers
        ''')

        # 2. Supprimer toutes les questions
        cursor.execute('''
            DELETE FROM questions
        ''')

        db_connection.commit()
        db_connection.close()

        return '', 204

    except Exception as e:
        db_connection.rollback()
        db_connection.close()
        return {'message': f'An error occurred: {e}'}, 500


def delete_all_scores(auth_token) -> tuple:
    if not auth_token:
        return 'Authorization token is missing', 401
    db_connection = sqlite3.connect(path)

    try:
        decode_token(auth_token)

        cursor = db_connection.cursor()
        cursor.execute('DELETE FROM scores')
        db_connection.commit()
        db_connection.close()
        return '', 204

    except Exception as e:
        db_connection.rollback()
        db_connection.close()
        return {'message': f'An error occurred: {e}'}, 500


def create_participation(payload) -> tuple:
    # Obtenez la taille du quiz (si nécessaire)
    quiz_size = get_quiz_info()[0]['size']

    # Si nécessaire, vérifiez que le nombre de réponses correspond à la taille du quiz
    if len(payload['answers']) != quiz_size:
        return '', 400

    db_connection = sqlite3.connect(path)
    player_answers = payload['answers']

    try:
        # Récupérer les bonnes réponses
        correct_answers = get_correct_answers()

        # Comparer les réponses du joueur avec les bonnes réponses
        matching_bool = list(map(lambda a, b: a == b, player_answers, correct_answers))

        # Calculer le score (nombre de réponses correctes)
        matching_count = sum(matching_bool)

        # Résumé des réponses (tuples de bonne réponse et correspondance)
        answers_summaries = [(correct_answers[i], matching_bool[i]) for i in range(len(correct_answers))]

        # Obtenez l'heure actuelle pour le timestamp
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Insérer dans la table scores
        cursor = db_connection.cursor()

        # Préparez la requête d'insertion
        cursor.execute('''
            INSERT INTO scores (player_name, score, date)
            VALUES (?, ?, ?)
        ''', (payload['playerName'], matching_count, timestamp))

        # Commit des changements dans la base de données
        db_connection.commit()

        # Vous pouvez maintenant retourner les données du joueur et le score
        data = {
            'answersSummaries': answers_summaries,
            'playerName': payload['playerName'],
            'score': matching_count,
            'timestamp': timestamp
        }

        db_connection.close()  # Fermer la connexion à la base de données

        return data, 200

    except Exception as e:
        db_connection.rollback()  # Annuler si erreur
        db_connection.close()  # Fermer la connexion
        return {'message': f'An error occurred: {e}'}, 500


def get_correct_answers() -> list:
    db_connection = sqlite3.connect(path)
    try:
        cursor = db_connection.cursor()

        # 1. Récupérer toutes les questions
        cursor.execute('SELECT question_id FROM questions')
        questions = cursor.fetchall()
        correct_answers = []

        for question in questions:
            question_id = question[0]

            # 2. Récupérer toutes les réponses pour cette question
            cursor.execute('''
                SELECT answer_id, is_correct FROM answers WHERE question_id = ?
            ''', (question_id,))
            answers = cursor.fetchall()

            # 3. Trouver la position de la bonne réponse
            correct_answer_position = None
            for idx, (answer_id, is_correct) in enumerate(answers, start=1):
                if is_correct:
                    correct_answer_position = idx
                    break

            if correct_answer_position is not None:
                # Ajouter la position de la bonne réponse à la liste
                correct_answers.append(correct_answer_position)
            else:
                # Ajouter None si aucune bonne réponse n'est trouvée
                correct_answers.append(None)

        db_connection.close()

        # Retourner la liste des positions des bonnes réponses pour chaque question
        return correct_answers

    except Exception as e:
        db_connection.close()
        return f'An error occurred: {e}'


def delete_one_question(question_id, auth_token) -> tuple:
    if not auth_token:
        return 'Authorization token is missing', 401
    db_connection = sqlite3.connect(path)

    try:
        decode_token(auth_token)

        cursor = db_connection.cursor()

        # 1. Récupérer la position de la question à supprimer
        cursor.execute('SELECT position FROM questions WHERE question_id = ?', (question_id,))
        question = cursor.fetchone()

        if not question:
            return {'message': 'Question not found'}, 404

        question_position = question[0]

        # 2. Supprimer les réponses associées à cette question
        cursor.execute('DELETE FROM answers WHERE question_id = ?', (question_id,))

        # 3. Supprimer la question avec l'ID donné
        cursor.execute('DELETE FROM questions WHERE question_id = ?', (question_id,))

        # 4. Mettre à jour les positions des questions restantes (si nécessaire)
        cursor.execute('''
            UPDATE questions
            SET position = position - 1
            WHERE position > ?
        ''', (question_position,))

        # Commit des changements dans la base de données
        db_connection.commit()

        # Fermer la connexion à la base de données
        db_connection.close()

        return '', 204

    except Exception as e:
        db_connection.rollback()  # Annuler la transaction en cas d'erreur
        db_connection.close()  # Fermer la connexion
        return {'message': f'An error occurred: {e}'}, 500
