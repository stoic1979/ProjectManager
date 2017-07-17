from flask import Flask, request, make_response, render_template
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
    templateData = {'title': 'Login PAge'}
    return render_template('home.html', **templateData)

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
    ret = {}
    try:
        company_name = request.form['company_name']
        company_email = request.form['company_email']
        manager_username = request.form['manager_username']
        password = request.form['password']
        confirm_password =request.form['confirm_password']
        if password == confirm_password:
            mdb.register(company_name, company_email, manager_username, password, confirm_password)
            ret['error'] = 0
            ret['msg'] = 'Manager Registered Successfully'
        else:
            ret['error'] = 1
            ret['msg'] = 'password is not match'
    except Exception as exp:
        ret['error'] = 2
        ret['msg'] = exp
        print(traceback.format_exc())
    return json.dumps(ret)


@app.route('/login', methods=['POST'])
def login():
    ret = {}
    try:
        company_email = request.form['company_email']
        password = request.form['password']
        if mdb.user_exists(company_email, password):

            # login successfully

            expiry = datetime.datetime.utcnow()\
                     + datetime.timedelta(minutes=30)
            token = jwt.encode({'company_email': company_email, 'exp': expiry},
                               app.config['secretkey'], algorithm='HS256')

            ret['msg'] = 'Login Successfull'
            ret['error'] = 0
            ret['token'] = token.decode('UTF-8')
        else:
            ret['msg'] = 'Login failed'
            ret['error'] = 1
    except Exception as exp:
        ret['msg'] = '%s' % exp
        ret['error'] = 1
        print(traceback.format_exc())
    return json.dumps(ret)


if __name__ == '__main__':
    app.run()
