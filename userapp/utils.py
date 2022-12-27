import copy
import jwt
from userapp import JWT_SECRET, JWT_ALGORITHM, db
from flask import request, jsonify


def generate_jwt_token(payload):
    """
    Function to generate jwt token using PyJWT package
    :param payload: dict
        - first_name
        - last_name
        - password
    :return: jwt token
    """
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    encoded_jwt = "Bearer " + encoded_jwt
    return encoded_jwt


def decode_jwt_token(encoded_jwt_token):
    """
    function to decode jwt token
    :param encoded_jwt_token:
    :return: user details
    """
    encoded_jwt_token = encoded_jwt_token.split(" ")[1]
    decoded_token = jwt.decode(encoded_jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM, ])
    return decoded_token


def validate_authorization_header(func):
    """
    Decorator method to authenticate users for accessing templates and Authorize users for updating and deleting the
    templates
    :param func: view methods
    :return: JSON response
    """
    def decorator(*args, **kwargs):
        access_denied_response = {"responseCode": 401, "responseMessage": "Access Denied"}

        def validate_user_permissions(token):
            token = token.split(" ")[1]
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM, ])
            decoded_token = {
                key: value for key, value in decoded_token.items()
                if key in ['first_name', 'last_name', 'email', 'permissions']
            }
            permissions = decoded_token.pop('permissions')

            user_data = db.fetch_user_data_by_email_name(decoded_token)

            if len(user_data) == 1:
                if func.__name__ == "process_templates_by_id" and \
                        kwargs['template_id'] in user_data[0].get('templates'):
                    return True
                elif func.__name__ == "process_templates":
                    if request.method == 'GET' and permissions.get('ViewTemplates') == 'Y':
                        return True
                    if request.method == 'POST':
                        return True
                else:
                    return False

        encoded_jwt_token = request.headers.get('Authorization')

        if encoded_jwt_token is None:
            response = copy.deepcopy(access_denied_response)
            response["responseData"] = "Please provide Authorization token "
            return jsonify(response)

        if validate_user_permissions(encoded_jwt_token):
            return func(*args, **kwargs)

        return jsonify(access_denied_response)

    decorator.__name__ = func.__name__
    return decorator
