import  os
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'mysql://root:tong960125@localhost:3306/graduate?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
UPLOADED_FILES_DEST = '/Users/tong/Desktop/FlaskPro/app/static/upload'
SECRET_KEY = os.urandom(24)