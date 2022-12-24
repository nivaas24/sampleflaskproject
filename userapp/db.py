import bcrypt
from userapp import mongo
from pymongo.errors import DuplicateKeyError


def register_user(user_data):
    email = mongo.db.users.find({"email": user_data['email']})
    if len(list(email)) > 0:
        return "Email already registered"
    users = mongo.db.users.find({"first_name": user_data['first_name'], "last_name": user_data['last_name']})
    if len(list(users)) > 0:
        return "User First name and Last name already exists"
    hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
    user_data['password'] = hashed_password
    user_data['templates'] = []
    print("Inserting New User Record....")
    mongo.db.users.insert_one(user_data)
    return "User Registered successfully"


def validate_login(user_data):
    user_result = list(mongo.db.users.find({"email": user_data['email']}))[0]
    jwt_payload = None
    if len(user_result) == 0:
        response = "Email does not exists"
    elif not (bcrypt.checkpw(user_data['password'].encode('utf-8'), user_result['password'])):
        response = "Invalid Credentials"
    else:
        response = "Login Success, Welcome {0}, {1}".format(user_result['first_name'], user_result['last_name'])
        jwt_payload = {key: value for key, value in user_result.items() if key in ['first_name', 'last_name', 'email']}
    return response, jwt_payload


def fetch_all_templates():
    templates = list(mongo.db.templates.find())
    for template in templates:
        template['template_id'] = template['_id']
        del template['_id']
    return templates


def fetch_template_by_id(template_id):
    template = list(mongo.db.templates.find({"_id": template_id}))[0]
    user = list(mongo.db.users.find({"templates": {'$eq': template_id}}, {'first_name': 1, 'last_name': 1, '_id': 0}))
    first_name = user[0]['first_name']
    last_name = user[0]['last_name']
    template['created_by'] = first_name + ", " + last_name
    return template


def insert_template(template_insert_data):
    try:
        response = mongo.db.users.insert_one(template_insert_data)
        insert_status = "Template Id: {} inserted successfully".format(response['insertedId'])
        print(insert_status)
    except DuplicateKeyError:
        return "Template already existing"


def update_template_by_id(template_id, template_data):
    template_filter = {"_id": template_id}
    updated_template = {
        "template_name": template_data['template_name'],
        "body": template_data['body'],
        "subject": template_data['subject']
    }
    result = mongo.db.templates.updateOne(template_filter, {'$set': updated_template})
    if result['matchedCount'] == 1 and result['modified_count'] == 1:
        return "Template Id: {} Updated successfully".format(template_id)
    return


def delete_template_by_id(template_id):
    template_filter = {"_id": template_id}
    result = mongo.db.templates.deleteMany(template_filter)
    if result['deletedCount'] == 1:
        return "Template Id: {} Deleted successfully".format(template_id)
    return


def fetch_user_data_by_email_name(filter_payload):
    result = list(mongo.db.users.find(filter_payload))
    return result





