from flask.ext.wtf import Form
from wtforms import fields
from wtforms.validators import Email, InputRequired, ValidationError


class UserForm(Form):
    email = fields.StringField(validators=[InputRequired(), Email()])
    password = fields.StringField(validators=[InputRequired()])

    def populate_object(self, user):
        user.set_password(self.password.data)
        user.email = self.email.data


class PostForm(Form):
    content = fields.StringField(validators=[InputRequired()])
    user_pk = fields.StringField(validators=[InputRequired()])

    def populate_object(self, post):
        post.content = self.content.data
        post.user_pk = self.user_pk.data