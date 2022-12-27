import bcrypt
from userapp import mongo
from pymongo.errors import DuplicateKeyError


def register_user(user_data):
    """
    DB function to validate and insert a new user record, the function will not register new user for the following
    conditions,
         1. if the combination of first name and last name already exists
         2. if email is already existing in the system
    password will be hashed before storing in db
    :param user_data: dict with first_name, last_name, email, password
    :return: status message in string
    """
    email = mongo.db.users.find({"email": user_data['email']})
    if len(list(email)) > 0:
        return "Email already registered"
    users = mongo.db.users.find({"first_name": user_data['first_name'], "last_name": user_data['last_name']})
    if len(list(users)) > 0:
        return "User First name and Last name already exists"
    hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
    user_data['password'] = hashed_password
    user_data['templates'] = []
    mongo.db.users.insert_one(user_data)
    return "User Registered successfully"


def validate_login(user_data):
    """
    DB function to authenticate user and return user data payload which will be further used to generate jwt token
    :param user_data: dict with email and password
    :return: response message, jwt_payload
    """
    user_result = list(mongo.db.users.find({"email": user_data['email']}))[0]
    jwt_payload = None
    if len(user_result) == 0:
        response = "Email does not exists"
    elif not (bcrypt.checkpw(user_data['password'].encode('utf-8'), user_result['password'])):
        response = "Invalid Credentials"
    else:
        response = "Login Success, Welcome {0}, {1}".format(user_result['first_name'], user_result['last_name'])
        jwt_payload = {key: value for key, value in user_result.items()
                       if key in ['first_name', 'last_name', 'email', 'permissions']}
    return response, jwt_payload


def fetch_all_templates():
    """
    DB function to fetch all templates
    :return: list of dict with all template data
    """
    templates = list(mongo.db.templates.find())
    for template in templates:
        template['template_id'] = template['_id']
        del template['_id']
    return templates


def fetch_template_by_id(template_id):
    """
    DB function to fetch template by template ID
    :param template_id:
    :return: dict of template data
    """
    template = list(mongo.db.templates.find({"_id": template_id}))
    if len(template) == 0:
        return template
    else:
        template = template[0]
    return template


def insert_template(template_insert_data, user_data):
    """
    DB function to insert template data in templates collection and add template id to templates array in users
    collection
    :param template_insert_data:
    :param user_data
    :return: status message
    """
    try:
        user_email = user_data.get('email')
        user_name = "{0} {1}".format(user_data.get('first_name'), user_data.get('last_name'))
        latest_template_id = list(mongo.db.templates.find({}, {"_id": 1}).sort([('_id', -1)]).limit(1))[0]['_id']
        latest_template_id = int(latest_template_id) + 1
        template_insert_data['_id'] = str(latest_template_id)
        template_insert_data['created_user'] = user_name
        mongo.db.templates.insert_one(template_insert_data)
        mongo.db.users.update_one({"email": user_email}, {"$push": {"templates": str(latest_template_id)}})
        insert_status = "Template Id: {} inserted successfully".format(latest_template_id)
        return insert_status
    except DuplicateKeyError:
        return "Template already existing"


def update_template_by_id(template_id, template_data):
    """
    DB function to update template by template ID
    :param template_id:
    :param template_data:
    :return: status message
    """
    template_filter = {"_id": template_id}
    updated_template = {
        "template_name": template_data['template_name'],
        "body": template_data['body'],
        "subject": template_data['subject']
    }
    mongo.db.templates.update_one(template_filter, {'$set': updated_template})
    return "Template Id: {} Updated successfully".format(template_id)


def delete_template_by_id(template_id, user_email):
    """
    DB function to delete template by template ID
    :param template_id:
    :return: status message if success, None if failed
    """
    template_filter = {"_id": template_id}
    mongo.db.templates.delete_many(template_filter)
    mongo.db.users.update_one({"email": user_email}, {"$pull": {"templates": template_id}})
    return "Template Id: {} Deleted successfully".format(template_id)


def fetch_user_data_by_email_name(filter_payload):
    """
    DB function to fetch user data by email and first_name, last_name
    :param filter_payload:
    :return:
    """
    result = list(mongo.db.users.find(filter_payload))
    return result


def update_permission(email, permission):
    mongo.db.users.update_one({"email": email}, {'$set': {'permissions.ViewTemplates': permission}})
    return 'User permission updated successfully'
