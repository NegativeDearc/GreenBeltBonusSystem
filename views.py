from flask import Flask,render_template,request,g,session,url_for,abort,redirect,flash,jsonify
from release_score import Action
from itertools import chain
import sqlite3
import string
import os

app = Flask(__name__)
app.secret_key = 'WELCOME TO SIX_SIGMA TEAM'

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
    print request.form
    res = None;total = None
    if request.method == 'POST':
        employee_name = request.form.get('employee_name','')
        if employee_name != '':
            SQL_SEARCH_MEMBER = '''SELECT PROJECT_NUMBER,
                                          PROJECT_NAME,
                                          PROJECT_DUE_TIME,
                                          ININTIALOR,
                                          LEADER,
                                          MAJOR_PARTICIPATOR,
                                          MINIOR_PARTICIPATOR,
                                          ACTIVE_SCORE
                                   FROM TOTAL
                                   WHERE LEADER
                                   LIKE "%%%s%%"
                                   OR ININTIALOR
                                   LIKE "%%%s%%"
                                   OR MAJOR_PARTICIPATOR
                                   LIKE "%%%s%%"
                                   OR MINIOR_PARTICIPATOR
                                   LIKE "%%%s%%;"
                                ''' % (tuple([employee_name]) * 4)
            cur = g.conn.cursor()
            res = cur.execute(SQL_SEARCH_MEMBER).fetchall()
    return render_template('root.html',data = res)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/admin',methods = ['GET','POST'])
def admin():
    print request.form
    if session.get('is_active',False) is not True:
        #actived until the web browser shut down
        #if want to logout,just let session['is_active']=False
        abort(401)

    #search the project reaching to the check point
    cur = g.conn.cursor()
    data_3_month = cur.execute('''SELECT PROJECT_NUMBER,
                                         PROJECT_NAME,
                                         CHECK_POINT_3_MONTH,
                                         LEADER,
                                         GOLDEN_IDEA_SCORE,
                                         PROJECT_SCORE,
                                         ACTIVE_SCORE
                                  FROM TOTAL
                                  WHERE DATE('now','+3 days') > CHECK_POINT_3_MONTH
                                  AND DATE('now','-3 days') < CHECK_POINT_3_MONTH
                                  AND ([3_MONTH_CHECK] != 1 OR [3_MONTH_CHECK] IS NULL);
                               ''').fetchall()
    data_6_month = cur.execute('''SELECT PROJECT_NUMBER,
                                         PROJECT_NAME,
                                         CHECK_POINT_6_MONTH,
                                         LEADER,
                                         GOLDEN_IDEA_SCORE,
                                         PROJECT_SCORE,
                                         ACTIVE_SCORE
                                  FROM TOTAL
                                  WHERE DATE('now','+3 days') > CHECK_POINT_6_MONTH
                                  AND DATE('now','-3 days') < CHECK_POINT_6_MONTH
                                  AND ([6_MONTH_CHECK] != 1 OR [6_MONTH_CHECK] IS NULL );
                               ''').fetchall()
    if request.method == 'POST':
        reverse_dict = dict(zip(request.form.values(),request.form.keys()))
        if request.form.get('sub1') == 'submit':
            #update values
            if request.form.get('update','') == 'on':
                #sqlite3 dynamic for type,it's ok use %s or ?
                cur = g.conn.cursor()
                UPDATE_PROJECT_INFO = '''UPDATE PROJECT_INFO
                                         SET PROJECT_NAME = "%s",PROJECT_DUE_TIME = "%s"
                                         WHERE PROJECT_NUMBER = "%s";
                                         '''% (request.form['project_name'],
                                               request.form['due_time'],
                                               request.form['project_num'])
                UPDATE_MEMBER_INFO = '''UPDATE MEMBER_INFO
                                        SET ININTIALOR = "%s",
                                            LEADER = "%s",
                                            MAJOR_PARTICIPATOR = "%s",
                                            MINIOR_PARTICIPATOR = "%s"
                                        WHERE PROJECT_NUMBER = "%s";
                                        ''' % (request.form['inintialor'],
                                               request.form['leader'],
                                               request.form['major_member'],
                                               request.form['minior_member'],
                                               request.form['project_num'])
                UPDATE_SCORE_INFO = ''' UPDATE SCORE_CARD
                                        SET GOLDEN_IDEA_LEVEL = "%s",
                                            PROJECT_SCORE_LEVEL = "%s"
                                        WHERE PROJECT_NUMBER = "%s";
                                        ''' % (request.form['s2'],
                                               request.form['s1'],
                                               request.form['project_num'])
                UPDATE_MEMBER_COUNT_MAJOR = '''UPDATE MEMBER_INFO
                                               SET MAJOR_PARTICIPATOR_COUNT = count_member(MAJOR_PARTICIPATOR)
                                               WHERE PROJECT_NUMBER = "%s"''' % request.form['project_num']
                UPDATE_MEMBER_COUNT_MAINIOR = '''UPDATE MEMBER_INFO
                                                 SET MINIOR_PARTICIPATOR_COUNT = count_member(MINIOR_PARTICIPATOR)
                                                 WHERE PROJECT_NUMBER = "%s"''' % request.form['project_num']

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
                INSERT_PROJECT_INFO = '''INSERT INTO
                                         PROJECT_INFO (PROJECT_NUMBER,PROJECT_NAME,PROJECT_DUE_TIME)
                                         VALUES ("%s","%s","%s");
                                         '''% (request.form['project_num'],
                                               request.form['project_name'],
                                               request.form['due_time'])
                INSERT_MEMBER_INFO = '''INSERT INTO
                                        MEMBER_INFO (PROJECT_NUMBER,
                                                     ININTIALOR,
                                                     LEADER,
                                                     MAJOR_PARTICIPATOR,
                                                     MINIOR_PARTICIPATOR,
                                                     MAJOR_PARTICIPATOR_COUNT,
                                                     MINIOR_PARTICIPATOR_COUNT)
                                        VALUES ("%s","%s","%s","%s","%s","%s","%s");
                                        ''' % (request.form['project_num'] ,
                                               request.form['inintialor'] ,
                                               request.form['leader'],
                                               request.form['major_member'],
                                               request.form['minior_member'],
                                               count_member(request.form['major_member']),
                                               count_member(request.form['minior_member']))
                INSERT_SCORE_INFO = ''' INSERT INTO
                                        SCORE_CARD (PROJECT_NUMBER,GOLDEN_IDEA_LEVEL,PROJECT_SCORE_LEVEL)
                                        VALUES ("%s","%s","%s");
                                        ''' % (request.form['project_num'],
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
    SEARCH_NAME = '''SELECT FORMAT_NAME
                     FROM USER_ID
                     WHERE NAME
                     LIKE "%%%s%%"
                     OR
                     ID LIKE "%%%s%%";''' % (n,n)
    res = cur.execute(SEARCH_NAME).fetchall()
    usr_name = list(chain(*res))
    return jsonify(dict(zip(string.lowercase,usr_name)))

if __name__ == '__main__':
    app.run(debug = True, port = 5010,threaded = True)
