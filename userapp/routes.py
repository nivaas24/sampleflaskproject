from flask import request, jsonify
from userapp import app, db, utils


success_response = {"responseCode": 200, "responseMessage": "Success"}
failure_response = {"responseCode": 404, "responseMessage": "Failed"}


@app.route("/register", methods=['POST'])
def user_registration():
    """
    View function to register a new user, this endpoint validates the first name, last name and email with
    existing user records and inserts new user record, password will be hashed before storing in db

    Request Body:
     - first_name
     - last_name
     - email
     - password

    :return: JSON response
    """
    user_data = request.get_json()
    response = failure_response
    try:
        registration_status = db.register_user(user_data)
        if registration_status == "User Registered successfully":
            response = success_response
        response['responseData'] = registration_status
    except Exception:
        response['responseData'] = "Unable to Process the Request"
    return jsonify(response)


@app.route("/login", methods=['POST'])
def user_login():
    """
    View function for user login, this endpoint authenticates the user and generates a JWT token
    Request Body:
     - email
     - password
    :return: JSON response with status message and Bearer token
    """
    user_data = request.get_json()
    response = failure_response
    try:
        login_status, jwt_payload = db.validate_login(user_data)
        if "Login Success" in login_status:
            response = success_response
        response['responseData'] = login_status
        response['AuthorizationToken'] = utils.generate_jwt_token(jwt_payload)
    except Exception:
        response['responseData'] = "Unable to Process the Request"
    return jsonify(response)


@app.route("/template", methods=['GET', 'POST'])
@utils.validate_authorization_header
def process_templates():
    """
    view function to get all templates and insert new templates, this function is wrapped by
    validate_authorization_header which validates the Bearer token from 'request.headers.Authorization' token from any
    registered user will pass the validation to get all templates and insert new templates.
    Request Body:
     - template_name
     - subject
     - body
    Request Header:
     - Authorization
    :return: response JSON with response message and data
    """
    response = failure_response
    if request.method == 'GET':
        try:
            templates = db.fetch_all_templates()
            response = success_response
            if len(templates) == 0:
                response['response_data'] = "No Templates Found"
            else:
                response['response_data'] = templates
        except Exception:
            response['response_data'] = "Unable to fetch templates"
        return response
    if request.method == 'POST':
        try:
            template_insert_data = request.get_json()
            jwt_token = request.headers.get('Authorization')
            user_email = utils.decode_jwt_token(jwt_token).get('email')
            template_insert_status = db.insert_template(template_insert_data, user_email)
            if "success" in template_insert_status:
                response = success_response
            response['responseData'] = template_insert_status
        except Exception:
            import traceback
            print(traceback.format_exc())
            response['responseData'] = "Unable to Process the Request"
        return response


@app.route("/template/<template_id>", methods=['GET', 'PUT', 'DELETE'])
@utils.validate_authorization_header
def process_templates_by_id(template_id):
    """
    vew function to get, update and delete templates by template id, this function is wrapped by
    validate_authorization_header which validates the Bearer token from 'request.headers.Authorization' token from any
    registered user which will pass the validation to get template by template id and only allow the owner of template
    the update and delete template.
    Request Body:(for update only)
      - template_name
      - subject
      - body
    Request Header:
      - Authorization
    :return: response JSON with response message and data
    """
    response = failure_response
    response_data = None
    if request.method == 'GET':
        try:
            template = db.fetch_template_by_id(template_id)
            response = success_response
            if len(template) == 0:
                response_data = "Template ID: {} not found".format(template_id)
            else:
                template['template_id'] = template['_id']
                del template['_id']
                response_data = template
        except Exception:
            import traceback
            print(traceback.format_exc())
            response_data = "Unable to fetch template {}".format(template_id)

    if request.method == "PUT":
        try:
            template_update_data = request.get_json()
            result = db.update_template_by_id(template_id, template_update_data)
            if result is None:
                response_data = "Template ID: {} not found".format(template_id)
            else:
                response = success_response
                response_data = result
        except Exception:
            import traceback
            print(traceback.format_exc())
            response_data = "Unable to update template {}". format(template_id)

    if request.method == "DELETE":
        try:
            result = db.delete_template_by_id(template_id)
            if result is None:
                response_data = "Template ID: {} not found".format(template_id)
            else:
                response = success_response
                response_data = result
        except Exception:
            response_data = "Unable to update template {}". format(template_id)
    response['responseData'] = response_data
    return response
