from flask import Flask, render_template
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

#create random secret key 
import os
SECRET_KEY = os.urandom(32)

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log in")

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login")
def secret():
    my_form = LoginForm()
    return render_template('login.html',form=my_form)

if __name__ == '__main__':
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(debug=True)