from flask import Flask,render_template,request,g,session,url_for,abort,redirect,flash,jsonify
from release_score import Action
from views_sql import views_sql
from totalSummary import totalSummary
from itertools import chain
import sqlite3
import string
import os

app = Flask(__name__)
app.secret_key = 'WELCOME TO SIX_SIGMA TEAM'
sql = views_sql()

def count_member(name):
    s = name.split(',')
    return len(s)

@app.before_request
def connect_db():
    #+'/CTLSS_BONUS_DB' in Linux or OSX
    path = os.path.abspath(os.path.dirname(__file__)) + '/CTLSS_BONUS_DB'
    g.conn = sqlite3.connect(path,timeout = 5)
    g.conn.text_factory=lambda x: unicode(x, "utf-8", "ignore")
    #register function
    g.conn.create_function('count_member',1,count_member)

def csrf_protect():
    if request.method == 'POST':
        token = session.pop('_csrf_token',None)
        if not token or token != request.form.get('_crsf_token'):
            abort(403)

def generate_csrf_token():
    if '_crsf_token' not in session:
        session['_crsf_token'] = os.urandom(15).encode('hex')
    return session['_crsf_token']

app.jinja_env.globals['crsf_token'] = generate_csrf_token

@app.route('/customer',methods = ['GET','POST'])
def customer():
    res = None;
    d0 = None;d1 = None;d2 = None;d3 = None;d4 = None
    d5 = None;d6 = None;d7 = None;d8 = None;d9 = None;
    d10 = None;d11 = None;d12 = None
    if request.method == 'POST':
        employee_name = request.form.get('employee_name','')
        if employee_name != '':
            search_member = sql.SQL_SEARCH_MEMBER % (tuple([employee_name]) * 4)
            cur = g.conn.cursor()
            res = cur.execute(search_member).fetchall()
            ts = totalSummary(employee_name)
            d0,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12 = ts.summary(g.conn)
    return render_template('root.html',data = res,d0 = d0,d1 = d1,d2 = d2,d3 = d3,d4 = d4,
                           d5 = d5,d6 = d6,d7 = d7,d8 = d8,d9 = d9,d10 =d10,d11 = d11,d12 =d12)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/admin',methods = ['GET','POST'])
def admin():
    if session.get('is_active',False) is not True:
        #actived until the web browser shut down
        #if want to logout,just let session['is_active']=False
        abort(401)

    #search the project reaching to the check point
    cur = g.conn.cursor()
    data_3_month = cur.execute(sql.data_3_month).fetchall()
    data_6_month = cur.execute(sql.data_6_month).fetchall()
    if request.method == 'POST':
        reverse_dict = dict(zip(request.form.values(),request.form.keys()))
        if request.form.get('sub1') == 'submit':
            #update values
            if request.form.get('update','') == 'on':
                #sqlite3 dynamic for type,it's ok use %s or ?
                cur = g.conn.cursor()
                UPDATE_PROJECT_INFO = sql.UPDATE_PROJECT_INFO \
                                      % (request.form['project_name'],
                                         request.form['due_time'],
                                         request.form['project_num'])
                UPDATE_MEMBER_INFO = sql.UPDATE_MEMBER_INFO % \
                                              (request.form['inintialor'],
                                               request.form['leader'],
                                               request.form['major_member'],
                                               request.form['minior_member'],
                                               request.form['project_num'])
                UPDATE_SCORE_INFO = sql.UPDATE_SCORE_INFO % \
                                              (request.form['s2'],
                                               request.form['s1'],
                                               request.form['project_num'])
                UPDATE_MEMBER_COUNT_MAJOR = sql.UPDATE_MEMBER_COUNT_MAJOR % request.form['project_num']
                UPDATE_MEMBER_COUNT_MAINIOR = sql.UPDATE_MEMBER_COUNT_MAINIOR % request.form['project_num']

                cur.execute(UPDATE_PROJECT_INFO)
                cur.execute(UPDATE_MEMBER_INFO)
                cur.execute(UPDATE_SCORE_INFO)
                cur.execute(UPDATE_MEMBER_COUNT_MAJOR)
                cur.execute(UPDATE_MEMBER_COUNT_MAINIOR)
                g.conn.commit()
                return redirect(url_for('admin'))
            #insert values
            else:
                cur = g.conn.cursor()
                INSERT_PROJECT_INFO = sql.INSERT_PROJECT_INFO % \
                                              (request.form['project_num'],
                                               request.form['project_name'],
                                               request.form['due_time'])
                INSERT_MEMBER_INFO = sql.INSERT_MEMBER_INFO % \
                                              (request.form['project_num'] ,
                                               request.form['inintialor'] ,
                                               request.form['leader'],
                                               request.form['major_member'],
                                               request.form['minior_member'],
                                               count_member(request.form['major_member']),
                                               count_member(request.form['minior_member']))
                INSERT_SCORE_INFO = sql.INSERT_SCORE_INFO % \
                                              (request.form['project_num'],
                                               request.form['s2'],
                                               request.form['s1'])

                cur.execute(INSERT_PROJECT_INFO)
                cur.execute(INSERT_MEMBER_INFO)
                cur.execute(INSERT_SCORE_INFO)
                g.conn.commit()
                return redirect(url_for('admin'))
        if reverse_dict.has_key('RELEASE3'):
            project_num = reverse_dict.get('RELEASE3')
            action = Action(g.conn,project_num,flag='3_MONTH')
            action.release_bonus()
            return redirect(url_for('admin'))
        if reverse_dict.has_key('CLOSE3'):
            project_num = reverse_dict.get('CLOSE3')
            action = Action(g.conn,project_num,flag='3_MONTH')
            action.close_prj()
            return redirect(url_for('admin'))
        if reverse_dict.has_key('RELEASE6'):
            project_num = reverse_dict.get('RELEASE6')
            action = Action(g.conn,project_num,flag='6_MONTH')
            action.release_bonus()
        if reverse_dict.has_key('CLOSE6'):
            project_num = reverse_dict.get('CLOSE6')
            action = Action(g.conn,project_num,flag='6_MONTH')
            action.close_prj()
            return redirect(url_for('admin'))
    return render_template('admin.html',data_3_month = data_3_month,data_6_month = data_6_month)

@app.route('/auth/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        session['usr'] = request.form.get('usr')
        session['pwd'] = request.form.get('pwd')
        if session['usr'] is not None and session['usr'] == 'admin':
            if session['pwd'] == 'admin':
                session['is_active'] = True
                return redirect(url_for('admin'))
            else:
                flash('Wrong User Name or Password')
        else:
            flash('Wrong User Name or Password')
    return render_template('login.html')

@app.route('/api/user/')
def user():
    n = request.args.get('term','')
    cur = g.conn.cursor()
    SEARCH_NAME = sql.SEARCH_NAME % (n,n)
    res = cur.execute(SEARCH_NAME).fetchall()
    usr_name = list(chain(*res))
    return jsonify(dict(zip(string.lowercase,usr_name)))

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True,threaded=True,port=5010)