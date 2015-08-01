from flask import Flask, request
from flask_restful import Resource, Api, abort
from models import ObjectManager, User
from elasticsearch import NotFoundError
from forms import UserForm

app = Flask(__name__)
api = Api(app)
SECRET_KEY = 'okokop'
app.debug = True

class UserResource(Resource):
    manager = ObjectManager(index='users', doc_type='user', model_class=User)

class UserView(UserResource):

    def get(self, user_pk):
        try:
            user = self.manager.find_one(user_pk)
        except NotFoundError:
            abort(404, message="User {} doesn't exist".format(user_pk))
        else:
            return {'email': user.email}

class UserListResource(UserResource):

    def get(self):
        return {'users': {user.pk:user.email for user in self.manager.find_all()}}

    def post(self):
        form = UserForm(request.form, csrf_enabled=False)
        if form.validate():
            user = User()
            form.populate_object(user)
            self.manager.save(user)
            return 200
        else:
            return 400


api.add_resource(UserListResource, '/users')
api.add_resource(UserView, '/user/<user_pk>')

