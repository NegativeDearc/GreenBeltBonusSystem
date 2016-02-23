from flask import Flask,render_template,request,g,session,url_for,abort,jsonify,redirect,flash
import sqlite3
import os
import json

app = Flask(__name__)
app.secret_key = 'WELCOME TO SIX_SIGMA TEAM'


@app.before_request
def connect_db():
    path = os.path.abspath(os.path.dirname(__file__)) + '\CLSS_BONUS_DB'
    g.conn = sqlite3.Connection(path)

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
            SQL_SEARCH_MEMBER = '''
                SELECT * FROM TOTAL WHERE LEADER LIKE "%%%s%%" OR
                MAJOR_PARTICIPATOR LIKE "%%%s%%" OR
                MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                ''' % (employee_name,employee_name,employee_name)
            cur = g.conn.cursor()
            res = cur.execute(SQL_SEARCH_MEMBER).fetchall()
    return render_template('root.html',data = res)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/admin',methods = ['GET','POST'])
def admin():
    if session.get('is_actived',False) is not True:
        #actived until the web browser shut down
        abort(401)
    if request.method == 'POST':
        print request.form
        cur = g.conn.cursor()
        INSERT_PROJECT_INFO = '''INSERT INTO PROJECT_INFO (PROJECT_NUMBER,PROJECT_NAME,PROJECT_DUE_TIME) VALUES ("%s","%s","%s");''' \
                              % (request.form['project_num'],request.form['project_name'],request.form['due_time'])
        INSERT_MEMBER_INFO = '''INSERT INTO MEMBER_INFO (PROJECT_NUMBER,ININTIALOR,LEADER,MAJOR_PARTICIPATOR,MINIOR_PARTICIPATOR) VALUES ("%s","%s","%s","%s","%s");'''\
                             % (request.form['project_num'] , request.form['inintialor'] , request.form['leader'],request.form['major_member'],request.form['minior_member'])
        INSERT_SCORE_INFO = ''' INSERT INTO SCORE_CARD (PROJECT_NUMBER,GOLDEN_IDEA_LEVEL,PROJECT_SCORE_LEVEL) VALUES ("%s","%s","%s");''' \
                            % (request.form['project_num'],request.form['s2'],request.form['s1'])
        cur.execute(INSERT_PROJECT_INFO)
        cur.execute(INSERT_MEMBER_INFO)
        cur.execute(INSERT_SCORE_INFO)
        g.conn.commit()
        return redirect(url_for('admin'))
    return render_template('admin.html')

@app.route('/auth/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        session['usr'] = request.form.get('usr')
        session['pwd'] = request.form.get('pwd')
        if session['usr'] is not None and session['usr'] == 'admin':
            if session['pwd'] == 'admin':
                session['is_actived'] = True
                return redirect(url_for('admin'))
            else:
                flash('Wrong User Name or Password')
        else:
            flash('Wrong User Name or Password')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug = True, port = 5010,threaded = True)
