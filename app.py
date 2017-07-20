from flask import Flask, request, render_template, jsonify, session
from functools import wraps
from wtforms.fields import SelectField
from db import Mdb
import jwt
import datetime
import json
import traceback

app = Flask(__name__)
mdb = Mdb()

app.config['secretkey'] = 'some-strong+secret#key'
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


def sumSessionCounter():
    try:
        session['counter'] += 1
    except KeyError:
        session['counter'] = 1


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'missing token!'})

        try:
            data = jwt.decode(token, app.config['secretkey'])
        except:
            return jsonify({'message': 'invalid token!'})

        return f(*args, **kwargs)

    return decorated


@app.route('/')
def home():
    templateData = {'title': 'Signup Page'}
    return render_template('index.html', **templateData)


@app.route('/signin')
def signin():
    templateData = {'title': 'Signin Page'}
    return render_template('signin.html', **templateData)

# its for testing


@app.route('/protected')
@token_required
def protected():
    return 'protected'


@app.route('/unprotected')
def unprotected():
    return 'unprotected'


@app.route('/register', methods=['POST'])
def register():
    try:
        company_name = request.form['company_name']
        company_email = request.form['company_email']
        manager_username = request.form['manager_username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            mdb.register(company_name, company_email, manager_username,
                         password, confirm_password)
            print('User is added successfully')
            templateData = {'title': 'Signin Page'}
        else:
            return render_template('signin.html', session=session)
    except Exception as exp:
        print(traceback.format_exc())
    return render_template('index.html', session=session)


@app.route('/login', methods=['POST'])
def login():
    ret = {}
    try:
        sumSessionCounter()
        company_email = request.form['company_email']
        password = request.form['password']
        if mdb.user_exists(company_email, password):
            # mdb.get_data(company_email)
            session['name'] = company_email
            # mdb.get_data(company_email)

            # login successfully

            expiry = datetime.datetime.utcnow() + datetime.\
                timedelta(minutes=30)
            token = jwt.encode({'company_email': company_email, 'exp': expiry},
                               app.config['secretkey'], algorithm='HS256')

            ret['msg'] = 'Login Successfull'
            ret['error'] = 0
            ret['token'] = token.decode('UTF-8')
            templateData = {'title': 'singin page'}
        else:
            return render_template('index.html', session=session)
    except Exception as exp:
        ret['msg'] = '%s' % exp
        ret['error'] = 1
        print(traceback.format_exc())
    # return jsonify(ret)
    return render_template('home.html', session=session)


@app.route('/clear')
def clearsession():
    session.clear()
    return render_template('index.html', session=session)
    # return redirect(request.form('/signin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
