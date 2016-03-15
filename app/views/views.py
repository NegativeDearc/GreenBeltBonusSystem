from flask import render_template, request, g, session, url_for, abort, redirect, flash, jsonify
from urlparse import urlparse,urljoin
from app import app

from app.ext.insert_records import insert_records
from app.ext.totalSummary import totalSummary
from app.ext.report_monthly import report_html
from app.ext.release_score import Action
from app.ext.views_sql import views_sql
from app.ext.newDict import newDict

from itertools import chain
from config import config

import sqlite3
import string
import os

sql = views_sql()
insert_records = insert_records()

def count_member(name):
    # in case of count '' as one element
    # use Regexp in HTML to make sure ',' will not end in a string
    # s = re.split('\s*,\s*',string)
    s = name.split(',')
    if s[-1] == '':
        return len(s)-1
    else:
        return len(s)


@app.before_request
def connect_db():
    path = config['development'].DATABASE_PATH
    g.conn = sqlite3.connect(path, timeout = 5)
    g.conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    # register function of sqlite3
    g.conn.create_function('count_member', 1, count_member)


def csrf_protect():
    if request.method == 'POST':
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_crsf_token'):
            abort(403)


def generate_csrf_token():
    if '_crsf_token' not in session:
        session['_crsf_token'] = os.urandom(15).encode('hex')
    return session['_crsf_token']


app.jinja_env.globals['crsf_token'] = generate_csrf_token


@app.route('/search', methods=['GET', 'POST'])
def search():
    res = None
    res2 = None

    if request.method == 'POST':
        employee_name = request.form.get('employee_name', '')
        if employee_name != '':
            search_member = sql.SQL_SEARCH_MEMBER % (tuple([employee_name]) * 4)
            cur = g.conn.cursor()
            res = cur.execute(search_member).fetchall()
            ts = totalSummary(employee_name)
            res2 = ts.summary(g.conn)
    return render_template('search.html', data=res, data2=res2)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # active until the web browser shut down
    # if want to logout,just let session['is_active']=False
    if not session.get('is_active'):
        return redirect(url_for('login'),code=401)
    # search the project reaching to the check point
    cur = g.conn.cursor()
    data_3_month = cur.execute(sql.data_3_month).fetchall()
    data_6_month = cur.execute(sql.data_6_month).fetchall()
    if request.method == 'POST':
        reverse_dict = dict(zip(request.form.values(), request.form.keys()))
        if request.form.get('sub1') == 'submit':
            # update values
            if request.form.get('update', '') == 'on':
                # sqlite3 dynamic for type,it's ok use %s or ?
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
            # insert values
            else:
                cur = g.conn.cursor()
                INSERT_PROJECT_INFO = sql.INSERT_PROJECT_INFO % \
                                      (request.form['project_num'],
                                       request.form['project_name'],
                                       request.form['due_time'])
                INSERT_MEMBER_INFO = sql.INSERT_MEMBER_INFO % \
                                     (request.form['project_num'],
                                      request.form['inintialor'],
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
                cur.execute(insert_records.prj_launch(golden_type=request.form['s2'],
                                                      prj_num=request.form['project_num']))
                g.conn.commit()
                return redirect(url_for('admin'))
        if reverse_dict.has_key('RELEASE3'):
            project_num = reverse_dict.get('RELEASE3')
            action = Action(g.conn, project_num, flag='3_MONTH')
            action.release_bonus()
            insert_records.insert_month_3_release(g.conn,project_num,'3 month checkpoint')
            return redirect(url_for('admin'))
        if reverse_dict.has_key('CLOSE3'):
            project_num = reverse_dict.get('CLOSE3')
            action = Action(g.conn, project_num, flag='3_MONTH')
            action.close_prj()
            insert_records.insert_month_3_release(g.conn,project_num,'3 month closed')
            return redirect(url_for('admin'))
        if reverse_dict.has_key('RELEASE6'):
            project_num = reverse_dict.get('RELEASE6')
            action = Action(g.conn, project_num, flag='6_MONTH')
            action.release_bonus()
            insert_records.insert_month_3_release(g.conn,project_num,'6 month checkpoint')
            return redirect(url_for('admin'))
        if reverse_dict.has_key('CLOSE6'):
            project_num = reverse_dict.get('CLOSE6')
            action = Action(g.conn, project_num, flag='6_MONTH')
            action.close_prj()
            insert_records.insert_month_3_release(g.conn,project_num,'6 month closed')
            return redirect(url_for('admin'))
    return render_template('admin.html', data_3_month=data_3_month, data_6_month=data_6_month)


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    def get_redirect_target():
        for target in request.values.get('next'), request.referrer:
            if not target:
                continue
            if is_safe_url(target):
                return target

    def is_safe_url(target):
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and \
               ref_url.netloc == test_url.netloc
    # url/?next=next
    # a bugs here,if next = /auth/login itself,it will redirect to itself
    next = get_redirect_target()
    if request.method == 'POST':
        session['usr'] = request.form.get('usr')
        session['pwd'] = request.form.get('pwd')
        if session['usr'] is not None and session['usr'] == 'admin':
            if session['pwd'] == 'admin':
                session['is_active'] = True
                return redirect(next)
            else:
                flash('Wrong User Name or Password')
        else:
            flash('Wrong User Name or Password')
    return render_template('login.html',next = next)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/report',methods=['GET','POST'])
def report():
    if not session.get('is_active'):
        return redirect(url_for('login'),code=401)
    # need route protect here,but conflict with 'admin'
    data = {};prj = {}
    summary = newDict(Major=0,Initiator=0,Leader=0,Minor=0,sum=0)
    if request.method == 'POST' and request.form.get('submit') == 'submit':
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        report = report_html(g.conn,date_begin,date_end)
        names = report.get_name()
        for name in names:
            prj[name] = list(chain(*report.prj_set(name)))
            data[name] = report.summary(name)
            summary = summary + newDict(report.summary(name))
            # rewrite the dict class to let dict can add with dict
    return render_template('report.html',data = data,prj = prj,summary = summary)

@app.route('/api/user/')
def user():
    n = request.args.get('term', '')
    cur = g.conn.cursor()
    SEARCH_NAME = sql.SEARCH_NAME % (n, n)
    res = cur.execute(SEARCH_NAME).fetchall()
    usr_name = list(chain(*res))
    return jsonify(dict(zip(string.lowercase, usr_name)))

@app.route('/api/project/')
def project_info():
    n = request.args.get('term','')
    cur = g.conn.cursor()
    SEARCH_PRJ_INFO = sql.SEARCH_PRJ_INFO % n
    res = cur.execute(SEARCH_PRJ_INFO).fetchone()
    if res is None:
        return jsonify({})
    else:
        return jsonify(zip(string.lowercase,res))
