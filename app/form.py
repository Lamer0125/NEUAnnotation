# -*-coding:utf-8-*-
from flask_wtf import FlaskForm,Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField,RadioField,DateField,IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange
from app.models import User
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app import files
class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()],render_kw={'class':"form-control"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={'class':"form-control"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    type = RadioField('type', choices=[('user','user'),('annotator','annotator')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class UploadForm(FlaskForm ):
    file = FileField(u'选择文件',validators=[
        FileAllowed(files,u'文件格式不正确'),
        FileRequired(u'文件未选择')])
    tag = StringField(u'待标注标签', validators=[DataRequired()])
    taskname = StringField(u'任务名', validators=[DataRequired()])
    introduce = StringField(u'任务介绍',validators = [DataRequired()])
    bonus = IntegerField(u'积分值',validators=[NumberRange(min=0, max=5)] )
    select = RadioField(u'任务类型',choices=[('single',u'单选'),('multi',u'多选')],validators=[DataRequired()])
    relation = BooleanField(u'关系标注')
    expiration = DateField(u'截止日期',format = '%Y-%m-%d',validators=[DataRequired()])
    submit = SubmitField(u'上传')

class AddForm(FlaskForm):
    file = FileField(validators=[
        FileAllowed(files,u'文件格式不正确'),
        FileRequired(u'文件未选择！')])
    taskname = StringField(u'任务名', validators=[DataRequired()])
    submit = SubmitField(u'上传')

class DeleteForm(FlaskForm):
    taskname = StringField(u'待删除任务名',validators = [DataRequired()])
    submit = SubmitField(u'确认')




