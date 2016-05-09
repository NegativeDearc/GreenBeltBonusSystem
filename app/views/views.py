# -*- coding:utf-8 -*-

from flask import render_template, request, g, session, url_for, abort, redirect, flash, jsonify, make_response
from urlparse import urlparse, urljoin
from app import app,db

from app.ext.rules import ruleMaker
from app.ext.func_collection import count_member, golden_score, project_score, active_score_launched
from app.ext.insert_records import insert_records
from app.ext.totalSummary import totalSummary
from app.ext.report_monthly import report_html
from app.ext.release_score import Action
from app.ext.views_sql import views_sql
from app.ext.newDict import newDict
from app.models.dbModels import usrPwd,usrName

from itertools import chain
from config import config

import sqlite3
import string
import os

sql = views_sql()


@app.before_request
def connect_db():
    # 请求之前打开数据库链接
    # 调用配置
    path = config['development'].DATABASE_PATH
    g.conn = sqlite3.connect(path, timeout=5)
    g.conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    # 注册函数
    g.conn.create_function('count_member', 1, count_member)
    g.conn.create_function('golden_score', 1, golden_score)
    g.conn.create_function('project_score', 1, project_score)
    g.conn.create_function('active_score_launched', 2, active_score_launched)


@app.teardown_appcontext
def close_db(exception):
    # 注意flask有两种环境，一种是应用环境app context，一种是请求环境request context
    # 在应用关闭销毁数据库链接
    if hasattr(g, 'conn'):
        # 打印查看关闭情况
        # print 'Database has been closed'
        g.conn.close()

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
    data = None;data2 = None
    if request.method == 'POST':
        employee_name = request.form.get('employee_name', '')
        if employee_name != '':
            ts = totalSummary(employee_name)
            data,data2 = ts.personal_score_matrix(g.conn)
    return render_template('search.html', data=data,data2=data2)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # session 过期时间 直到浏览器退出
    # 若要登出用户，使 session['is_active']=False
    if not session.get('is_active'):
        return redirect(url_for('login'), code=401)
    # 查找到达检查点的项目
    cur = g.conn.cursor()
    data_3_month = cur.execute(sql.data_3_month).fetchall()
    data_6_month = cur.execute(sql.data_6_month).fetchall()
    # 注意，insert_records 读取配置文件，记录写入数据库
    # 若在/admin以外初始化，一旦配置文件被/rules修改，配置文件仍旧还是修改前
    # 请在此初始化，以读取最新的配置表
    insert = insert_records()
    # 提交表单
    if request.method == 'POST':
        print request.form
        print request.form.get('prj_name')
        return redirect(url_for('admin'))
    return render_template('admin.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    def get_redirect_target():
        for target in request.values.get('next'), request.referrer:
            if not target:
                continue
            if target:
                return target

    # 使用nginx后，reuquest.host_url将是服务器的地址
    # 然而app是在localhost运行的，这里无法判断target
    # 如何解决？          
    def is_safe_url(target):
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and \
               ref_url.netloc == test_url.netloc

    next = get_redirect_target()
    if request.method == 'POST':
        # 如果查询到用户则返回app.Models.dbModels.usrPwd类,可调用该类的方法
        # 注意这边使用user = request.form.get('usr')还是使用user == request.form.get('usr'),为什么?
        usr = usrPwd.query.filter_by(user = request.form.get('usr')).first()
        if usr is not None and usr.verify_pwd(request.form.get('pwd')):
            session['is_active'] = True
            return redirect(next)
        else:
            flash('Wrong User Name or Password')
    return render_template('login.html', next=next)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/report', methods=['GET', 'POST'])
def report():
    if not session.get('is_active'):
        return redirect(url_for('login'), code=401)

    data = {};prj = {}
    summary = newDict(Major=0, Initiator=0, Leader=0, Minor=0, sum=0)
    if request.method == 'POST' and request.form.get('submit') == 'submit':
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        report = report_html(g.conn, date_begin, date_end)
        names = report.get_name()
        for name in names:
            prj[name] = list(chain(*report.prj_set(name)))
            data[name] = report.summary(name)
            summary = summary + newDict(report.summary(name))
    return render_template('report.html', data=data, prj=prj, summary=summary)


@app.route('/rules', methods=['GET', 'POST'])
def rules():
    if not session.get('is_active'):
        return redirect(url_for('login'), code=401)
    rul = ruleMaker()
    data = rul.rules_api_info()
    if request.method == 'POST':
        # 更新本地json配置文件
        rul.update_config(request.form)
        return redirect(url_for('rules'))
    return render_template('rules.html', data=data)


@app.route('/api/user/')
def user():
    n = request.args.get('term', '')
    content = "%%%s%%" % n
    res = db.session.query(usrName.format_name).filter(usrName.format_name.ilike(content)).all()
    usr_name = list(chain(*res))
    return jsonify(dict(zip(string.lowercase, usr_name)))

@app.route('/api/project/')
def project_info():
    n = request.args.get('term', '')
    cur = g.conn.cursor()
    SEARCH_PRJ_INFO = sql.SEARCH_PRJ_INFO % n
    res = cur.execute(SEARCH_PRJ_INFO).fetchone()
    if res is None:
        return jsonify({})
    else:
        return jsonify(zip(string.lowercase, res))


@app.route('/api/rules/')
def rules_api():
    rul = ruleMaker()
    return jsonify(rul.rules_api_info())


@app.route('/api/add_employee/')
def add_employee():
    id = request.args.get('id', None)
    name = request.args.get('name', None)
    if id is not None and name is not None:
        try:
            res = usrName(id=id,name=name)
            db.session.add(res)
            db.session.commit()
        except Exception:
            return make_response('', 500)
        else:
            return make_response('', 200)
    else:
        return make_response('', 500)
