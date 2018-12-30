
from app import db,login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    type = db.Column(db.String(120),index=True)
    credits = db.Column(db.Integer,nullable= True, default=0)
    password_hash = db.Column(db.String(128))
    def __repr__(self):
        return '<User %r>' % (self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def set_type(self,type):
        self.type = type
    def add_credits(self):
        self.credits=self.credits+1
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Data(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    filename = db.Column(db.String(30))
    url =db.Column(db.String(200),index = True,unique=True)
    type=db.Column(db.String(64),index= True)
    taskid =db.Column(db.Integer)
    def __init__(self,filename,url,type,taskid):
        self.filename =filename
        self.url=url
        self.type=type
        self.taskid=taskid


class Task(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    taskname = db.Column(db.String(100),unique= True,nullable=False)
    userid = db.Column(db.Integer,nullable=False)
    select =db.Column(db.String(30),nullable= False)
    relation = db.Column(db.Boolean,nullable=False)
    expiration = db.Column(db.Date,nullable=False)
    tag = db.Column(db.String(200),index=True,nullable=False)
    introduce = db.Column(db.String(200),nullable= False)
    bonus =db.Column(db.Integer,nullable=False,index=True)
    def __init__(self,taskname,userid,select,relation,expiration,tag,introduce,bonus):
        self.taskname = taskname
        self.select =select
        self.relation =relation
        self.expiration = expiration
        self.userid = userid
        self.tag = tag
        self.introduce = introduce
        self.bonus = bonus


class Result(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    annotator = db.Column(db.Integer)
    dataid = db.Column(db.Integer)
    tag = db.Column(db.String(200),index= True)
    def __init__(self, annotator, dataid,tag):
        self.annotator = annotator
        self.dataid = dataid
        self.tag = tag

class Result_relation(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    annotatorid = db.Column(db.Integer)
    taskid = db.Column(db.Integer)
    tag = db.Column(db.String(200),index=True)
    def __init__(self,annotatorid,taskid,tag):
        self.annotatorid = annotatorid
        self.taskid = taskid
        self.tag = tag
class Final(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annotator = db.Column(db.Integer)
    dataid = db.Column(db.Integer)
    tag = db.Column(db.String(200), index=True)

    def __init__(self, annotator, dataid, tag):
        self.annotator = annotator
        self.dataid = dataid
        self.tag = tag
    def set_tag(self,tag):
        self.tag = tag
class Final_relation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annotatorid = db.Column(db.Integer)
    taskid = db.Column(db.Integer)
    tag = db.Column(db.String(200), index=True)

    def __init__(self, annotatorid, taskid, tag):
        self.annotatorid = annotatorid
        self.taskid = taskid
        self.tag = tag
    def set_tag(self,tag):
        self.tag =tag