from flask import Flask, request
from flask_restful import Resource, Api, abort
from models import ObjectManager, User, Post, Model
from elasticsearch import NotFoundError
from forms import UserForm, PostForm
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
SECRET_KEY = 'dontnowhowdisablecrsf'
auth = HTTPBasicAuth()

user_manager = ObjectManager(index=Model.index, doc_type=User.doc_type, model_class=User)
post_manger = ObjectManager(index=Model.index, doc_type=Post.doc_type, model_class=Post)

def get_model_or_404(manager, pk):
    try:
        model = manager.find_one(pk)
    except NotFoundError:
        abort(404, message="Entity not found")
    else:
        return model


@auth.verify_password
def verify_pw(username, password):
    try:
        user = user_manager.find_one(username)
    except NotFoundError:
        return None
    else:
        return user.verify_password(password)

class UserView(Resource):

    def get(self, user_pk):
        user = get_model_or_404(user_manager, user_pk)
        return {'email': user.email, 'password': user.user_password}

class UserListResource(Resource):

    def get(self):
        return [{'email': user.email} for user in user_manager.find_all()]

    def post(self):
        form = UserForm(request.form, csrf_enabled=False)
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
        form = PostForm(request.form, csrf_enabled=False)
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
        user = get_model_or_404(user_manager, post.user_pk)
        if user.email != auth.username():
            abort(401, message="Not user post")
        else:
            form = PostForm(request.form, csrf_enabled=False)
            if form.validate():
                form.populate_object(post)
                post_manger.update(post)
                return 200
            else:
                return 400


api.add_resource(UserListResource, '/users')
api.add_resource(UserView, '/user/<user_pk>')
api.add_resource(PostList, '/posts')
api.add_resource(PostView, '/post/<post_pk>')

