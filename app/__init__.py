import json
from flask import Flask, request
from flask_restful import Resource, Api, abort
from flask_wtf import Form
from .models import ObjectManager, User, Post, Model
from elasticsearch import NotFoundError
from .forms import UserForm, PostForm
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
api = Api(app)
auth = HTTPBasicAuth()

user_manager = ObjectManager(index='flask_blog', doc_type='user', model_class=User)
post_manger = ObjectManager(index='flask_blog', doc_type='post', model_class=Post)

def get_model_or_404(manager, pk):
    try:
        model = manager.find_one(pk)
    except NotFoundError:
        abort(404, message="Entity not found")
    else:
        return model

def is_user_himself(user_pk):
    user = get_model_or_404(user_manager, pk=user_pk)
    if user.email != auth.username():
        abort(403, message="Forbidden")
    else:
        return True


@auth.verify_password
def verify_pw(username, password):
    try:
        user = user_manager.find_one(username)
    except (ValueError, NotFoundError):
        return None
    else:
        return user.verify_password(password)

class UserView(Resource):

    def get(self, user_pk):
        user = get_model_or_404(user_manager, user_pk)
        return {'email': user.email}

    @auth.login_required
    def delete(self, user_pk):
        if is_user_himself(user_pk):
            user_manager.delete(user_pk)
        return 200

class UserListResource(Resource):

    def get(self):
        return [{'email': user.email} for user in user_manager.find_all()]

    def post(self):
        form = UserForm(request.form)
        if form.validate():
            user = User()
            form.populate_object(user)
            user_manager.save(user)
            return 200
        else:
            return 400


class PostList(Resource):

    @auth.login_required
    def post(self):
        form = PostForm(request.form)
        if form.validate():
            post = Post()
            post.user_pk = auth.username()
            form.populate_object(post)
            post_manger.save(post)
            return 200
        else:
            return 400

    def get(self):
        return [{'post_pk': post.pk, 'content': post.content, 'user_pk': post.user_pk} for post in post_manger.find_all()]

class PostView(Resource):

    def get(self, post_pk):
        post = get_model_or_404(post_manger, post_pk)
        return {'user_pk': post.user_pk, 'content': post.content}

    @auth.login_required
    def put(self, post_pk):
        post = get_model_or_404(post_manger, post_pk)
        if is_user_himself(post.user_pk):
            form = PostForm(request.form)
            if form.validate():
                form.populate_object(post)
                post_manger.update(post)
                return 200
            else:
                return 400

    @auth.login_required
    def delete(self, post_pk):
        post = get_model_or_404(post_manger, post_pk)
        if is_user_himself(post.user_pk):
            post_manger.delete(post.pk)
        return 200

api.add_resource(UserListResource, '/users')
api.add_resource(UserView, '/user/<user_pk>')
api.add_resource(PostList, '/posts')
api.add_resource(PostView, '/post/<post_pk>')

