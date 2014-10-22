from functools import wraps
import random
import string
import bcrypt
import requests
from flask import request, abort, g
from flask.ext.restful import Resource
from . import TokenModel, UserModel

def auth(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Auth-Token')

        if token is None:

              abort(403)

        else:

            if TokenModel.select().where(TokenModel.token == token).count() != 1:

                  abort(403)

            else:

                token = TokenModel.get(TokenModel.token == token)
                user = UserModel.get(UserModel.id == token.user)

                g.user = user

        return function(*args, **kwargs)
    return wrapper

class AuthenticatedResource (Resource):

    method_decorators = [auth]

class Authenticate (Resource):

    def post (self):

        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:

            username = username.encode('utf-8')
            password = password.encode('utf-8')

        else:

            abort(400)

        def verify (username, password):

            try:

                user = UserModel.get(UserModel.username == username)
                computed = user.password.encode('utf-8')

                if bcrypt.hashpw(password, computed) == computed:

                    return True

            except Exception:

                pass

            return False

        if not verify(username, password):

            abort(403)

        else:

            token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
            user = UserModel.get(UserModel.username == username)

            address = ''

            try:

                address = request.headers.getlist('X-Forwarded-For')[0]

            except Exception:

                address = request.remote_addr

            if address == '127.0.0.1':

            	  address = '46.19.37.108'

            r = requests.get('http://www.telize.com/geoip/%s' % address)

            TokenModel.create(
                token = token,
                user = user,
                address = address,
                user_agent = request.headers['User-Agent'],
                location = r.json()['country_code']
            )

            return {'token': token}
