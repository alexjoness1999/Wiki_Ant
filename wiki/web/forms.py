"""
    Forms
    ~~~~~
"""

from wtforms import RadioField
from wtforms import FileField
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError

from wiki.core import clean_url
from wiki.web import current_wiki
from wiki.web import current_users



class URLForm(FlaskForm):
    url = StringField('', [InputRequired()])

    def validate_url(form, field):
        if current_wiki.exists(field.data):
            raise ValidationError('The URL "%s" exists already.' % field.data)

    def clean_url(self, url):
        return clean_url(url)


class SearchForm(FlaskForm):
    term = StringField('', [InputRequired()])

    search_option = RadioField('Search Option', choices=[('tags', 'Search by Tags'),
                                                         ('title', 'Search by Title'),
                                                         ('body', 'Search by Body')])
    ignore_case = BooleanField(
        description='Ignore Case',
        # FIXME: default is not correctly populated
        default=True)


class EditorForm(FlaskForm):
    title = StringField('', [InputRequired()])
    body = TextAreaField('', [InputRequired()])
    tags = StringField('')
    photo = FileField('Image File')


class LoginForm(FlaskForm):
    username = StringField('', [InputRequired()])
    password = PasswordField('', [InputRequired()])

    def validate_username(form, field):
        user = current_users.get_user(form.username.data)
        if user is None:
            raise ValidationError('This username does not exist.')
        else:
            return

    def validate_password(form, field):
        user = current_users.get_user(form.username.data)
        if not user:
            return
        if not user.check_password(form.password.data):
            raise ValidationError('Username and password do not match.')


class RegisterForm(FlaskForm):
    fname = StringField('fname', [InputRequired()])
    lname = StringField('lname', [InputRequired()])
    email = StringField('email', [InputRequired()])
    username = StringField('user_name', [InputRequired()])
    password = PasswordField('password', [InputRequired()])
    submit = SubmitField('Register')

    def validate_username(form, field):
        user = current_users.get_user(form.username.data)
        if user is not None:
            raise ValidationError('This username is already exist.')
        else:
            current_users.add_user(form.fname.data, form.lname.data, form.email.data, form.username.data, form.password.data)


class EditProfileForm(FlaskForm):
    fname = StringField('First Name', [InputRequired()])
    lname = StringField('Last Name', [InputRequired()])
    email = StringField('Email Addresses', [InputRequired()])
    phone = StringField('Phone Number', [InputRequired()])
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')

    def validate_username(form, field):
        same_user = current_users.get_user(current_user.username)
        user = current_users.get_user(form.username.data)
        if user is None or same_user.username == user.username:
            return
        if user is not None:
            raise ValidationError('This username is already exist.')
