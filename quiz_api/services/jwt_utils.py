import jwt
import datetime
from werkzeug.exceptions import Unauthorized


class JwtError(Exception):
    """Exception raised for jwt errors in the quiz app 
    """

    def __init__(self, message="Jwt error"):
        self.message = message
        super().__init__(self.message)


secret = "Groupe Gregoire Titouan Hugo"
expiration_in_seconds = 3600


def build_token():
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration_in_seconds),
            'iat': datetime.datetime.utcnow(),
            'sub': 'quiz-app-admin'
        }
        return jwt.encode(
            payload,
            secret,
            algorithm="HS256"
        )
    except Exception as e:
        return e


def decode_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        token = auth_token[len("Bearer "):] if auth_token.startswith("Bearer ") else auth_token
        payload = jwt.decode(token, secret, algorithms="HS256")

        # if decoding did not fail, this means we are correctly logged in
        return payload['sub']
    except jwt.ExpiredSignatureError:
        print("Le token a expiré.")
    except jwt.InvalidTokenError as e:
        print(f"Erreur de décodage du token: {e}")
    except Exception as e:
        print(f"Une erreur inconnue est survenue: {e}")
