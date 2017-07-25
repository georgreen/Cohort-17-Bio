"""Simple app to register members to cohort 17 and count them."""

import os
import re

from flask import Flask, jsonify, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


# models
class Description(db.Model):
    """Model User descriptions."""

    __tablename__ = "descriptions"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(db.Model):
    """Model users in the DB."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    second_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    description = db.relationship(
        'Description', uselist=False, cascade="all, delete-orphan")

    def __init__(self, first_name, second_name, email, description):
        """Initialize the user object."""
        self.first_name = first_name
        self.second_name = second_name
        self.email = email
        self.description = Description(description=description)

    def __repr__(self):
        """Repr representation for user object."""
        return "<User {}>".format(self.first_name + " " + self.second_name)


# form
class RegisterForm(FlaskForm):
    """Form for registration."""

    first_name = StringField('First Name', validators=[DataRequired()])
    second_name = StringField('Second Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


# add commands
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)


# routes
@app.route("/")
def home():
    return render_template('index.html')


@app.route("/register", methods=('GET', 'POST'))
def register():
    """Main app logic."""
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        second_name = form.second_name.data
        email = form.email.data
        description = form.description.data

        if not (validate_names(first_name) and validate_names(second_name)):
            return "Invalid user name"
        if not create_user(email, first_name, second_name, description):
            return "User exists already"
        return "{} You joined corhort 17 succesfully".format(
            first_name + " " + second_name)

    return render_template('index1.html', form=form)


@app.route("/totalusers")
def get_user_count():
    """Return total users in DB."""
    return jsonify({"total": len(User.query.all())})


def create_user(email, first_name, second_name, description):
    """A user creation factory methid."""
    if not User.query.filter_by(email=email).first():
        new_user = User(
            email=email,
            first_name=first_name,
            second_name=second_name,
            description=description)
        db.session.add_all([new_user, new_user.description])
        db.session.commit()
        return True
    return False


def validate_names(name):
    """Utility function to validate user names."""
    return re.match("^[A-Za-z0-9]+\s?[A-Za-z0-9]+$", name)


if __name__ == '__main__':
    manager.run()
