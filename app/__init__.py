from flask import Flask, request
from flask_restful import Resource, Api, abort
from models import ObjectManager, User, Post, Model
from elasticsearch import NotFoundError
from forms import UserForm, PostForm

app = Flask(__name__)
api = Api(app)
SECRET_KEY = 'okokop'
app.debug = True

class UserManagerMixin(object):
    manager = ObjectManager(index=Model.index, doc_type=User.doc_type, model_class=User)

class UserView(Resource, UserManagerMixin):

    def get(self, user_pk):
        try:
            user = self.manager.find_one(user_pk)
        except NotFoundError:
            abort(404, message="User {} doesn't exist".format(user_pk))
        else:
            return {'email': user.email, 'password': user.user_password}

class UserListResource(Resource, UserManagerMixin):

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


class PostManagerMixin(object):
    manager = ObjectManager(index=Model.index, doc_type=Post.doc_type, model_class=Post)


class PostList(Resource, PostManagerMixin):

    def post(self):
        form = PostForm(request.form, csrf_enabled=False)
        if form.validate():
            post = Post()
            form.populate_object(post)
            self.manager.save(post)
            return 200
        else:
            return 400

    def get(self):
        return {'posts': {posts.pk:{'content': posts.content, 'user_pk': posts.user_pk} for posts in self.manager.find_all()}}

class PostView(Resource, PostManagerMixin):

    def get(self, post_pk):
        try:
            post = self.manager.find_one(post_pk)
        except NotFoundError:
            abort(404, message="Post {} doesn't exist".format(post_pk))
        else:
            return {'user_pk': post.user_pk, 'content': post.content}

api.add_resource(UserListResource, '/users')
api.add_resource(UserView, '/user/<user_pk>')
api.add_resource(PostList, '/posts')
api.add_resource(PostView, '/post/<post_pk>')

