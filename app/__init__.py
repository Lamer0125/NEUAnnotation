from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, TEXT,patch_request_class
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
login = LoginManager(app)
login.session_protection='strong'
login.login_view = 'login'
files = UploadSet('files',IMAGES+TEXT)
configure_uploads(app, files)
patch_request_class(app)
fileList = []
from app import models,routes


