from flask import Flask,render_template,request,g,session,redirect,url_for,abort
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'WELCOME TO SIX_SIGMA TEAM'


@app.before_request
def connect_db():
    path = os.path.abspath(os.path.dirname(__file__)) + '/Bonus.db'
    print path,url_for('customer')
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
            SQL_SEARCH_MEMBER = '''SELECT * FROM BONUS WHERE PROJECT_LEADER= "%s" OR PROJECT_MEMBER= "%s"''' % (employee_name,employee_name)
            #SQL_LEADER_BONUS = '''SELECT SUM(LEADER_BONUS) FROM BONUS WHERE PROJECT_LEADER= "%s"''' % employee_name
            #SQL_MEMBER_BONUS = '''SELECT SUM(MEMBER_BONUS) FROM BONUS WHERE PROJECT_LEADER= "%s"''' % employee_name
            cur = g.conn.cursor()
            res = cur.execute(SQL_SEARCH_MEMBER).fetchall()
    return render_template('root.html',data = res)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True, port = 5010)
