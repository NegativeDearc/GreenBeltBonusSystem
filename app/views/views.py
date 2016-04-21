# -*- coding:utf-8 -*-

from flask import render_template, request, g, session, url_for, abort, redirect, flash, jsonify, make_response
from urlparse import urlparse, urljoin
from app import app

from app.ext.rules import ruleMaker
from app.ext.func_collection import count_member, golden_score, project_score, active_score_launched
from app.ext.insert_records import insert_records
from app.ext.totalSummary import totalSummary
from app.ext.report_monthly import report_html
from app.ext.release_score import Action
from app.ext.views_sql import views_sql
from app.ext.newDict import newDict
from app.ext.hash_password import passwordSecurity

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
    data = None
    data2 = None
    if request.method == 'POST':
        employee_name = request.form.get('employee_name', '')
        if employee_name != '':
            # search_member = sql.SQL_SEARCH_MEMBER % (tuple([employee_name]) * 4)
            # cur = g.conn.cursor()
            # res = cur.execute(search_member).fetchall()
            # ts = totalSummary(employee_name)
            # res2, res3 = ts.summary(g.conn)
            ts = totalSummary(employee_name)
            data,data2 = ts.personal_score_matrix(g.conn)
    return render_template('search.html', data=data,data2 = data2)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    rul = ruleMaker()
    data = rul.rules_api_info()
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
    # 仍存在bug，被修改后再次提交的数据，insert_records()不能响应
    if request.method == 'POST':
        reverse_dict = dict(zip(request.form.values(), request.form.keys()))
        if request.form.get('sub1') == 'submit':
            # 注意这段只有在request.form 包含指定数据才有效，否则http 400
            golden_type = rul.golden_type_judging(request.form)
            # update values
            if request.form.get('update', '') == 'on':
                # sqlite3 使用动态类型判断，字段拼接用 ? 或者 %s
                # 注意 request 表单是不可修改的
                # 注意防止SQL注入
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
                                      request.form['project_num'],
                                      count_member(request.form['major_member']),
                                      count_member(request.form['minior_member']))
                UPDATE_SCORE_INFO = sql.UPDATE_SCORE_INFO % \
                                    (golden_type,
                                     request.form['s1'],
                                     golden_score(golden_type),
                                     project_score(request.form['s1']),
                                     request.form['targeted_incentive_score'],
                                     request.form['duplicability'],
                                     request.form['resource_usage'],
                                     request.form['implement_period'],
                                     request.form['kpi_impact'],
                                     request.form['cost_saving'],
                                     active_score_launched(golden_type,
                                                           request.form['s1'],
                                                           request.form['targeted_incentive_score']),
                                     request.form['project_num'])

                # 更新之前项目初始化的信息
                insert.prj_launch(project_type=request.form['s1'],
                                  prj_num=request.form['project_num'],
                                  conn=g.conn,
                                  update=True)
                # 执行其他表的更新
                cur.execute(UPDATE_PROJECT_INFO)
                cur.execute(UPDATE_MEMBER_INFO)
                cur.execute(UPDATE_SCORE_INFO)
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
                                     golden_type,
                                     request.form['s1'],
                                     golden_score(golden_type),
                                     project_score(request.form['s1']),
                                     request.form['targeted_incentive_score'],
                                     request.form['duplicability'],
                                     request.form['resource_usage'],
                                     request.form['implement_period'],
                                     request.form['kpi_impact'],
                                     request.form['cost_saving'],
                                     active_score_launched(golden_type,
                                                           request.form['s1'],
                                                           request.form['targeted_incentive_score']))
                # 数据库已设置项目编号唯一性，否则回滚
                # 产生500错误
                # 注意提交顺序以及是否需要两次提交
                cur.execute(INSERT_PROJECT_INFO)
                cur.execute(INSERT_MEMBER_INFO)
                cur.execute(INSERT_SCORE_INFO)
                insert.prj_launch(project_type=request.form['s1'],
                                  prj_num=request.form['project_num'],
                                  conn=g.conn)
                return redirect(url_for('admin'))
        if reverse_dict.has_key('RELEASE3'):
            project_num = reverse_dict.get('RELEASE3')
            action = Action(g.conn, project_num, flag='3_MONTH')
            action.release_bonus()
            insert.insert_release_detail(conn=g.conn, prj_num=project_num, flag=1)
            return redirect(url_for('admin'))
        if reverse_dict.has_key('CLOSE3'):
            project_num = reverse_dict.get('CLOSE3')
            action = Action(g.conn, project_num, flag='3_MONTH')
            action.close_prj()
            insert.insert_release_detail(g.conn, project_num, flag=3)
            return redirect(url_for('admin'))
        if reverse_dict.has_key('RELEASE6'):
            project_num = reverse_dict.get('RELEASE6')
            action = Action(g.conn, project_num, flag='6_MONTH')
            action.release_bonus()
            insert.insert_release_detail(g.conn, project_num, flag=2)
            return redirect(url_for('admin'))
        if reverse_dict.has_key('CLOSE6'):
            project_num = reverse_dict.get('CLOSE6')
            action = Action(g.conn, project_num, flag='6_MONTH')
            action.close_prj()
            insert.insert_release_detail(g.conn, project_num, flag=4)
            return redirect(url_for('admin'))
    return render_template('admin.html', data_3_month=data_3_month, data_6_month=data_6_month, data=data)


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
    # 初始化密码hash检查模块
    password_security = passwordSecurity(g.conn)
    if request.method == 'POST':
        rv = password_security.verify_hash_password(request.form.get('usr'),
                                                    request.form.get('pwd'))
        if rv:
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
    # need route protect here,but conflict with 'admin'
    data = {}
    prj = {}
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
            # rewrite the dict class to let dict can add with dict
    return render_template('report.html', data=data, prj=prj, summary=summary)


@app.route('/rules', methods=['GET', 'POST'])
def rules():
    if not session.get('is_active'):
        return redirect(url_for('login'), code=401)
    rul = ruleMaker()
    data = rul.rules_api_info()
    if request.method == 'POST':
        # print request.form
        # 更新本地json配置文件
        rul.update_config(request.form)
        return redirect(url_for('rules'))
    return render_template('rules.html', data=data)


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
        sql = '''INSERT INTO USER_ID (ID,NAME)
                 VALUES ("%s","%s");''' % (id, name)
        cur = g.conn.cursor()
        try:
            cur.execute(sql)
        except Exception:
            return make_response('', 500)
        else:
            return make_response('', 200)
        finally:
            g.conn.commit()
    else:
        return make_response('', 500)
