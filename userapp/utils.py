import jwt
from userapp import JWT_SECRET, JWT_ALGORITHM, db
from flask import request, jsonify


def generate_jwt_token(payload):
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    encoded_jwt = "Bearer " + encoded_jwt
    return encoded_jwt


def validate_authorization_header(func):
    def decorator(*args, **kwargs):
        encoded_jwt_token = request.headers.get('Authorization').split(" ")[1]
        decoded_token = jwt.decode(encoded_jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM,])
        decoded_token = {
            key: value for key, value in decoded_token.items() if key in ['first_name', 'last_name', 'email']
        }
        user_data = db.fetch_user_data_by_email_name(decoded_token)
        if len(user_data) == 1:
            if func.__name__ == "process_templates_by_id" and request.method in ['PUT', 'DELETE']:
                if kwargs['template_id'] in user_data[0].get('templates'):
                    response = func(*args, **kwargs)
                else:
                    response = {
                        "responseCode": 401, "responseMessage": "AccessDenied",
                        "responseData": "User does not have permission to update or delete template"
                    }
            else:
                response = func(*args, **kwargs)
        else:
            response = {"responseCode": 401, "responseMessage": "UnAuthorized User"}
        return jsonify(response)
    decorator.__name__ = func.__name__
    return decorator
