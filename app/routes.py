# -*-coding:utf-8-*-
from flask import render_template, flash, redirect,url_for,request,session
from flask_login import login_user, logout_user, current_user, login_required
from flask_uploads import IMAGES,TEXT
from app import app,db
from app import files,fileList
from werkzeug.urls import url_parse
from app.form import LoginForm,RegistrationForm,UploadForm,AddForm,DeleteForm
from app.models import User,Task,Data,Result,Result_relation,Final,Final_relation
from sqlalchemy import  func
from sqlalchemy import desc
import os
import time
import hashlib
from collections import defaultdict
import  math
from  operator import  itemgetter
from sqlalchemy import distinct
@app.route('/')
@app.route('/index')
def index():
    type = session.get('type')
    return render_template("index.html", title='Home', type=type)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You have already logined')
        type = session.get('type')
        return redirect(url_for('upload'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #print type(user.type)
        session['type'] = user.type
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        #print 'login:',request
        '''
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        '''
        session['username'] = form.username.data
        #return redirect(next_page)
        if user.type =='user':
            return redirect(url_for('upload'))
        else:
            Task_user = [task for task in Task.query.order_by(Task.id).all()]
            type = session.get('type')
            username = session.get('username')
            user = User.query.filter_by(username=username).first()
            recom_list = recommondation(user.id, get_userdict())
            re = []
            for recom in recom_list:
                task = Task.query.filter_by(id=recom[0]).first()
                data = Data.query.filter_by(taskid =recom[0]).filter_by(type ='photo').first()
                tu=(task.taskname,data.url)
                re.append(tu)
            print re
            return render_template('task.html', Task=Task_user, title='Task', type=type,recommond_task= re)
    return render_template('login.html',
                           title='Sign In',
                           form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.set_type(form.type.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/upload",methods=['GET','POST'])
@login_required
def upload():
    form = UploadForm()
    urls=[]
    Type = session.get('type')
    username =session.get('username')
    if form.validate_on_submit():
        #print 'dddd'
        i=0
        #print form.expiration.data,
        print form.relation.data
        if form.relation.data == True:
            file_num = len(request.files.getlist('file'))
            print file_num
            if file_num  > 2:
                flash(u'关系类标注每次只能上传两张')
                return render_template('upload.html', form=form, title='Upload', type=Type)
        if Task.query.filter_by(taskname = form.taskname.data).first() != None:
            flash(u'任务名重复，请更换任务名！')
            return render_template('upload.html', form=form, title='Upload', type=Type)
        user = User.query.filter_by(username = username).first()
        task = Task(form.taskname.data,user.id,form.select.data,form.relation.data,form.expiration.data,form.tag.data,form.introduce.data,
                    form.bonus.data)
        #print task
        db.session.add(task)
        db.session.commit()
        for name in request.files.getlist('file'):
            filename = hashlib.md5('users' + str(time.time())).hexdigest()[:15]
            file = files.save(name, name=filename + '.')
            extension = file.split(".")[-1]
            #print extension
            if extension in list(IMAGES):
                type1 = 'photo'
            else:
                type1 = 'text'
            data = Data(file,files.url(file),type1,task.id)
            db.session.add(data)
            db.session.commit()
            #urls=urls.append(data.url)
        return  render_template('upload.html', form=form,title = 'Upload',type =Type,username =username)
    return render_template('upload.html', form=form,title = 'Upload',type =Type,username = username)


@app.route("/add",methods=['GET','POST'])
@login_required
def add():
    #print '-----------------aaaa'
    form = AddForm()
    type = session.get('type')
    username = session.get('username')
    if form.validate_on_submit():
        #print '-----------------bbbb'
        #print 'myFile',request.files.getlist('photo')
        task = Task.query.filter_by(taskname=form.taskname.data).first()
        if task==None:
            flash('This task does not exist!')
            return redirect(url_for('add'))
        elif task.relation == True:
            flash(u'关系类标注不能填加数据')
            redirect(url_for('add'))

        else:
            for name in request.files.getlist('file'):
                # print 'in'
                filename = hashlib.md5('users' + str(time.time())).hexdigest()[:15]
                file = files.save(name, name=filename + '.')

                extension = file.split(".")[-1]
                # print extension
                if extension in list(IMAGES):
                    type1 = 'photo'
                else:
                    type1 = 'text'
                data = Data(file, files.url(file), type1, task.id)
                db.session.add(data)
                db.session.commit()

    return render_template('add.html', title = 'Add',form=form,type = type,username =username)

@app.route("/delete",methods=['GET','POST'])
@login_required
def delete():
    form = DeleteForm()
    type = session.get('type')
    username = session.get('username')
    if form.validate_on_submit():
        task = Task.query.filter_by(taskname = form.taskname.data).first()
        if task == None:
            flash('Wrong task name!')
        else:
            db.session.delete(task)
            db.session.commit()
            data = Data.query.filter_by(taskid = task.id).all()
            for i in data:
                db.session.delete(i)
                db.session.commit()
                filename = i.url.split('/')[-1]
                path ='/Users/tong/Desktop/FlaskPro/app/static/upload/'
                os.remove(os.path.join(path,filename))
    return render_template('delete.html',form =form,title = 'Delete',type =type,username = username)
@app.route("/task1",methods=['GET','POST'])
@login_required
def Show_task():
    type =session.get('type')
    username  =  session.get('username')
    user = User.query.filter_by(username = username).first()
    tasknames = [ task.taskname for task in Task.query.filter_by(userid =user.id).all()]
    return  render_template('task_user.html',tasknames = tasknames,title = 'Task',type = type,username =username)


@app.route("/task",methods=['GET','POST'])
@login_required
def Select_task():
    #form = TaskForm()
    #form.task.choices = [(task.id,task.taskname) for task in Task.query.order_by(Task.id).all()]
    Task_user = [task for task in Task.query.order_by(Task.id).all()]
    type = session.get('type')
    username = session.get('username')
    user = User.query.filter_by(username = username).first()
    recom_list = recommondation(user.id, get_userdict())
    re =[]
    for recom in recom_list:
        task = Task.query.filter_by(id=recom[0]).first()
        data = Data.query.filter_by(taskid=recom[0]).filter_by(type='photo').first()
        tu = (task.taskname, data.url)
        re.append(tu)
    #print re
    return render_template('task.html', Task =Task_user,title = 'Task', type = type,recommond_task= re)

@app.route("/show",methods=['GET','POST'])
@login_required
def show():
    type = session.get('type')
    #print type
    taskname = request.args.get('task')
    # form = Tags()

    task = Task.query.filter_by(taskname=taskname).first()
    # print task
    select =task.select
    tags = task.tag.split(',')
    relation = task.relation
    # form.tag.choices = [(tag, tag) for tag in tags]
    page = request.args.get('page', 1, type=int)
    contents = []
    if relation == False:
        datas = Data.query.filter_by(taskid=task.id).paginate(page, 1, False)
        datatype = datas.items[0].type
        datatype2 = None
        datatype1 = None
        if datatype == 'text':

            for data in datas.items:
                file_object = open(os.path.join('/Users/tong/Desktop/FlaskPro/app/static/upload/', data.filename))
                try:
                    contents.append(file_object.read())
                finally:
                    file_object.close()

        next_url = url_for('show', task=taskname, page=datas.next_num) \
            if datas.has_next else None
        prev_url = url_for('show', task=taskname, page=datas.prev_num) \
            if datas.has_prev else None
    else:
        datas = Data.query.filter_by(taskid=task.id).all()
        datatype =None
        datatype1 = datas[0].type
        datatype2 = datas[1].type
        if datatype1 == 'text':


            file_object = open(os.path.join('/Users/tong/Desktop/FlaskPro/app/static/upload/', datas[0].filename))
            try:
                contents.append(file_object.read())
            finally:
                file_object.close()
        if datatype2 == 'text':


            file_object = open(os.path.join('/Users/tong/Desktop/FlaskPro/app/static/upload/', datas[1].filename))
            try:
                contents.append(file_object.read())
            finally:
                file_object.close()
        next_url = None
        prev_url = None

    annotator = session.get('username')
    #print annotator
    Annotator = User.query.filter_by(username=annotator).first()
    # print request.args.get('submit').encode('utf-8')
    if request.args.get('submit') != None:
        submit_str = request.args.get('submit').encode('utf-8')
        if submit_str == '提交':
            if select =='single':
                tag = request.args.get('tag')
                #print tag
                #print annotator
                if relation == False:
                    url = request.args.get('url')
                    # print urlm
                    data = Data.query.filter_by(url=url).first()
                    print data
                    result = Result(Annotator.id, data.id, tag)
                    db.session.add(result)
                    db.session.commit()
                    final_tag = db.session.query(Result.tag).filter_by(dataid=data.id).group_by(Result.tag).order_by(
                        desc(func.count(Result.id))).first()[0]
                    if Final.query.filter_by(dataid =data.id).first()!=None:
                        final_result = Final.query.filter_by(dataid =data.id).first()
                        final_result.set_tag(final_tag)
                    else:
                        final_result =Final(Annotator.id, data.id, final_tag)
                        db.session.add(final_result)
                        db.session.commit()

                else:
                    result = Result_relation(Annotator.id,task.id,tag)
                    db.session.add(result)
                    db.session.commit()
                    final_tag_relation = db.session.query(Result_relation.tag).filter_by(taskid=task.id).group_by(
                        Result_relation.tag).order_by(desc(func.count(Result_relation.id))).first()[0]
                    if Final_relation.query.filter_by(taskid =task.id).first()!=None:
                        final_relation_result = Final_relation.query.filter_by(taskid =task.id).first()
                        final_relation_result.set_tag(final_tag_relation)
                    else:
                        final_relation_result = Final_relation(Annotator.id, task.id, final_tag_relation)
                        db.session.add(final_relation_result)
                        db.session.commit()

            else:
                for index in range(len(tags)):
                    if request.args.get('tag' + str(index)) != None:
                        tag = request.args.get('tag' + str(index))
                        #print tag
                        if relation == False:
                            url = request.args.get('url')
                            print 'url', url
                            data = Data.query.filter_by(url=url).first()
                            print 'data', data
                            result = Result(Annotator.id, data.id, tag)
                            db.session.add(result)
                            db.session.commit()
                        else:
                            result = Result_relation(Annotator.id, task.id, tag)
                            db.session.add(result)
                            db.session.commit()
                if  relation == False:
                    db_num = db.session.query(func.count(distinct(Result.tag))).filter_by(dataid = data.id).first()
                    print 'num',db_num
                    if db_num[0] >= 3:
                        final_tag_list = db.session.query(Result.tag).filter_by(dataid=data.id).group_by(
                            Result.tag).order_by(desc(func.count(Result.id))).limit(3).all()
                        print 'list',final_tag_list
                        final_tag_str = final_tag_list[0][0] + ',' + final_tag_list[1][0] + ',' + final_tag_list[2][0]
                        # print 'final',final_tag_str
                    else:
                        final_tag_list = db.session.query(Result.tag).filter_by(dataid=data.id).all()
                        print 'sss',final_tag_list
                        if len(final_tag_list)==1:
                            final_tag_str = final_tag_list[0][0]
                        else:
                            final_tag_str = final_tag_list[0][0]+','+final_tag_list[1][0]
                    if Final.query.filter_by(dataid =data.id).first()!=None:
                        final_result = Final.query.filter_by(dataid =data.id).first()
                        final_result.set_tag(final_tag_str)
                    else:
                        final_result =Final(Annotator.id, data.id, final_tag_str)
                        db.session.add(final_result)
                        db.session.commit()
                else:
                    db_num = db.session.query(func.count(distinct(Result_relation.tag))).filter_by(dataid=data.id).first()
                    if db_num >= 3:
                        final_relation_tag_list = db.session.query(Result_relation.tag).filter_by(taskid=task.id).group_by(
                            Result_relation.tag).order_by(desc(func.count(Result_relation.id))).limit(3).all()
                        # print 'kkkkkkkkkk',final_relation_tag_list[0][0]
                        final_tag_relation_str = final_relation_tag_list[0][0] + ',' + final_relation_tag_list[1][0]+ ',' + final_relation_tag_list[2][0]
                    else:
                        final_relation_tag_list = db.session.query(Result_relation.tag).filter_by(taskid =task.id).all()
                        if len(final_relation_tag_list) ==1:
                            final_tag_relation_str =final_relation_tag_list[0][0]
                        else:
                            final_tag_relation_str = final_relation_tag_list[0][0]+final_relation_tag_list[1][0]
                    if Final_relation.query.filter_by(taskid = task.id).first()!=None:
                        final_relation_result = Final_relation.query.filter_by(taskid =task.id).first()
                        final_relation_result.set_tag(final_tag_relation_str)
                    else:
                        final_relation_result = Final_relation(Annotator.id, task.id, final_tag_relation_str)
                        db.session.add(final_relation_result)
                        db.session.commit()
            Annotator.add_credits()

    # print 'jkjk',request.args.get('tag')
    # print data

    return render_template('show.html', datas=datas, tags=tags, taskname=taskname, page=page,select =select,relation =relation,
                           next_url=next_url, prev_url=prev_url, type=type,contents = contents,datatype =datatype,
                           datatype1=datatype1,datatype2 = datatype2)

@app.route('/showuser',methods=['GET','POST'])
@login_required
def show_user():
    type =session.get('type')
    #print type
    taskname = request.args.get('task')
    # form = Tags()
    task = Task.query.filter_by(taskname=taskname).first()
    # print task
    select = task.select
    relation = task.relation
    #print select
    #tags = task.tag.split(',')

    # form.tag.choices = [(tag, tag) for tag in tags]

    datas = Data.query.filter_by(taskid=task.id).all()
    #print type(datas)
    #print datas

    contents = []

    Tag =[]
    if task.relation == False:
        datatype = datas[0].type
        datatype1 = None
        datatype2 = None
        if datatype == 'text':
            for data in datas:
                file_object = open(os.path.join('/Users/tong/Desktop/FlaskPro/app/static/upload/', data.filename))
                try:
                    contents.append(file_object.read())
                finally:
                    file_object.close()
        for data in datas:
            if select == 'single':
                print data.id
                tag = db.session.query(Final.tag).filter_by(dataid =data.id).first()
                print tag[0]
                Tag.append(tag[0])
                print Tag[0]
            else:
                tag = db.session.query(Final.tag).filter_by(dataid = data.id).first()
                tag_list = tag[0].split(',')
                Tag.append(tag_list)
                print Tag
    else:
        datatype =None
        datatype1 = datas[0].type
        datatype2 = datas[1].type
        if datatype1 == 'text':

            file_object = open(os.path.join('/Users/tong/Desktop/FlaskPro/app/static/upload/', datas[0].filename))
            try:
                contents.append(file_object.read())
            finally:
                file_object.close()
        if datatype2 == 'text':
            file_object = open(os.path.join('/Users/tong/Desktop/FlaskPro/app/static/upload/', datas[1].filename))
            try:
                contents.append(file_object.read())
            finally:
                file_object.close()
        if select == 'single':
            tag = db.session.query(Final_relation.tag).filter_by(taskid = task.id).first()
            Tag =tag[0]
            # print Tag
        else:
            tag = db.session.query(Final_relation.tag).filter_by(taskid = task.id).first()
            #print tag[0]
            #print type(tag)
            Tag = tag[0].split(',')
            # print Result_list
            # print Tag
    return render_template('show_user.html',datas=datas,taskname =taskname, tag=Tag, contents=contents, type=type,select =select,
                           relation = relation,datatype=datatype,datatype1 =datatype1,datatype2 =datatype2)
@app.route('/personal',methods=['GET','POST'])
@login_required
def personal():
    type = session.get('type')
    username = session.get('username')
    print 'username',username,len(username)
    user = User.query.filter_by(username =username).first()
    rank_list = db.session.query(User.username).filter_by(type ='annotator').order_by(desc(User.credits)).all()
    print 'aaa',rank_list
    for index,item in enumerate(rank_list):
        print 'item',item[0],len(item[0])
        if item[0] == username:
            print '00000'
            rank=index+1
            break
    result_list = Result.query.filter_by(annotator =user.id).all()
    result_relation = Result_relation.query.filter_by(annotatorid = user.id).all()
    #print result_relation
    task_list=[]
    if result_list != None:
        for result in result_list:
            data = Data.query.filter_by(id=result.dataid).first()
            task = Task.query.filter_by(id=data.taskid).first()
            if task not in task_list:
                task_list.append(task)
            #print 'aaa',task_list
    if result_relation != None:
        for result in result_relation:
            task = Task.query.filter_by(id=result.taskid).first()
            if task not in task_list:
                task_list.append(task)
                #print 'bbb',task_list
    #print task_list

    return render_template('personal.html',type = type,username = username,email = user.email,bonus = user.credits,rank =rank,
                           task_list=task_list)
def get_userdict():
    user_dict =dict()
    seq =[ annotator.id for annotator in User.query.filter_by(type ='annotator').all()]
    for user in seq:
        per_value = []
        for result in Result.query.filter_by(annotator=user).all():
            data = Data.query.filter_by(id = result.dataid).first()
            if data.taskid not in per_value:
                per_value.append(data.taskid)
                #print user,per_value
        for result in Result_relation.query.filter_by(annotatorid=user).all():
            if result.taskid  not in per_value:
                per_value.append(result.taskid)
                #print 'pers',per_value
        user_dict[user]=per_value
    return user_dict
#建立物品倒排表,计算物品相似度u
def itemCF(user_dict):
    N=dict()
    C=defaultdict(defaultdict)
    W=defaultdict(defaultdict)
    for key in user_dict:
        for i in user_dict[key]:
            if i not in N.keys():
                N[i]=0
            N[i]+=1               #N[i]表示标注过某任务的用户数
            for j in user_dict[key]:
                if i==j:
                    continue
                if j not in C[i].keys():
                    C[i][j]=0
                C[i][j]+=1      ##C[i][j]表示都标注过i，j任务的用户数
    for i,related_item in C.items():
        for j,cij in related_item.items():
            W[i][j]=cij/math.sqrt(N[i]*N[j])##表示两个任务间的相似度
    #print 'N',N
    #print 'C',C
    return W

def recommondation(user_id,user_dict):
    rank=defaultdict(int)
    l=list()
    W=itemCF(user_dict)
    print 'bbb',W
    for i in user_dict[user_id]: #i为特定用户的标注过的任务id
        for j,wj in sorted(W[i].items(),key=itemgetter(1),reverse=True): #sorted()的返回值为list
            if j in user_dict[user_id]:
                continue
            print 'ddddd'
            rank[j]+=wj
    print 'rank',rank
    l=sorted(rank.items(),key=itemgetter(1),reverse=True)[0:3]
    print 'lll',l
    return l
