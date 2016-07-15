# -*- coding:utf-8 -*-

from flask import render_template, request, g, session, url_for, abort, redirect, \
    flash, jsonify, make_response
from urlparse import urlparse, urljoin
from app import app, db

from app.ext.rules import ruleMaker
from app.ext.func_collection import register_mem_info
from app.ext.report import ReportDetail
from app.models.dbModels import usrPwd, usrName, prjInfo, prjMem, ScoreRelease, SearchDetail

from itertools import chain
from config import config

import sqlite3
import string
import os


@app.before_request
def connect_db():
    # 请求之前打开数据库链接
    # 调用配置
    path = config['development'].DATABASE_PATH
    g.conn = sqlite3.connect(path, timeout=5)
    g.conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    # 注册函数


@app.teardown_appcontext
def close_db(exception):
    # 注意flask有两种环境，一种是应用环境app context，一种是请求环境request context
    # 在应用关闭销毁数据库链接
    if hasattr(g, 'conn'):
        g.conn.close()
    db.session.close()


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
    content = None
    total   = None
    if request.method == 'POST':
        if request.form.get('date_begin',None):
            session['date_begin_2'] = request.form.get('date_begin')
            session['date_end_2']   = request.form.get('date_end')
        if request.form.get('employee_name',None):
            content, total = SearchDetail(request.form).score_detail()
    return render_template('search.html',data = content,data2 = total)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('is_active'):
        return redirect(url_for('login'), code=401)
    # 载入配置表,渲染到html页面
    res = ruleMaker().rules_api_info()
    # 查找到达检查点的项目
    data = db.session.query(prjInfo).all()
    data_3_month = [x for x in data if x.data_3_month != -1]
    data_6_month = [x for x in data if x.data_6_month != -1]

    if request.method == 'POST':
        print request.form
        # 反转request.form
        reverse_dict = dict(zip(request.form.values(), request.form.keys()))
        #
        if request.form.get('submit1') == 'Submit':
            db.session.add(prjInfo(request.form))
            x, y = register_mem_info(request.form)
            for ele in x:
                db.session.add(prjMem(*ele, **y))
            ScoreRelease(request.form.get('prj_name')).prj_launch(request.form)
            return redirect(url_for('admin'))

        # 3个月的动作
        if 'RELEASE' in reverse_dict:
            for x in data_3_month:
                if x.prj_no == reverse_dict.get('RELEASE'):
                    x.pass_3_month
            ScoreRelease(reverse_dict.get('RELEASE')).prj_3_release()
            return redirect(url_for('admin'))
        if 'CLOSE' in reverse_dict:
            for x in data_3_month:
                if x.prj_no == reverse_dict.get('CLOSE'):
                    x.close_3_month
            ScoreRelease(reverse_dict.get('CLOSE')).prj_3_close()
            return redirect(url_for('admin'))

        # 6个月的动作
        if 'release' in reverse_dict:
            for x in data_6_month:
                if x.prj_no == reverse_dict.get('release'):
                    x.pass_6_month
            ScoreRelease(reverse_dict.get('release')).prj_6_release()
            return redirect(url_for('admin'))

        if 'close' in reverse_dict:
            for x in data_6_month:
                if x.prj_no == reverse_dict.get('close'):
                    x.close_6_month
            ScoreRelease(reverse_dict.get('close')).prj_6_close()
            return redirect(url_for('admin'))
    return render_template('admin.html',
                           res=res,
                           data_3_month=data_3_month,
                           data_6_month=data_6_month)


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    def get_redirect_target():
        for target in request.values.get('next'), request.referrer:
            if not target:
                continue
            if target:
                return target

    # 使用nginx后，request.host_url将是服务器的地址
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
        usr = usrPwd.query.filter_by(user=request.form.get('usr')).first()
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

    name = []
    score = {}
    content = {}
    summary = {}
    if request.method == 'POST' and request.form.get('submit') == 'submit':
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        name = ReportDetail(date_begin, date_end).name_set()
        score, summary = ReportDetail(date_begin, date_end).score_detail()
        content = ReportDetail(date_begin, date_end).record_detail()
    return render_template('report.html', score=score, name=name, content=content, summary=summary)


@app.route('/rules', methods=['GET', 'POST'])
def rules():
    if not session.get('is_active'):
        return redirect(url_for('login'), code=401)
    rul = ruleMaker()
    data = rul.rules_api_info()
    if request.method == 'POST':
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
    SEARCH_PRJ_INFO = '''SELECT * FROM project_total WHERE prj_no="%s"''' % n
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
            res = usrName(id=id, name=name)
            db.session.add(res)
            db.session.commit()
            return make_response('', 200)
        except Exception:
            return make_response('', 500)
    else:
        return make_response('', 500)


@app.route('/api/advanced_search/',methods=['POST','GET'])
def advanced_search():
    if request.method == 'POST':
        sql_text = request.form.get('sql')
        print sql_text

        from config import ProductionConfig
        conn = sqlite3.Connection(ProductionConfig.DATABASE_PATH)
        cur = conn.cursor()

        try:
            data = cur.execute('select * from project_total WHERE ' + sql_text)
            data = [list(x) for x in data]
            return jsonify({'data':data}),200
        except Exception:
            return abort(500)
        finally:
            cur.close()
            conn.close()
        # 解析sql使其能被sqlalchemy处理
    else:
        return jsonify({'GET':'GOT NOTHING'})