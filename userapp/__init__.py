import os
import sys
import configparser
from flask import Flask
from flask_pymongo import PyMongo


# load environment profile from flask run command args
#environment = sys.argv[1]
environment = "dev"

# set config file name and read configs from .ini file
file_name = 'appconfig.ini'
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config",  environment, file_name))
config = configparser.ConfigParser()
config.read(config_path)
db_config = dict(config.items('MONGO_CONFIG'))
DB_URI = \
    db_config['db_uri'].format(db_config['user_name'], db_config['password'], db_config['host'], db_config['db_name'])
flask_config = dict(config.items('FLASK_CONFIG'))
FLASK_DEBUG_MODE = flask_config['debug_mode']
JWT_SECRET = flask_config['jwt_secret_key']
JWT_ALGORITHM = flask_config['jwt_algorithm']


# create Flask app and load configs
app = Flask(__name__)
app.config['DEBUG'] = FLASK_DEBUG_MODE
app.config['MONGO_URI'] = DB_URI


# create PyMongo instance from flask_pymongo
mongo = PyMongo(app)

# import routes to load views
from userapp import routes
