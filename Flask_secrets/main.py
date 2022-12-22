from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email,Length

#create random secret key 
import os
SECRET_KEY = os.urandom(32)

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(),Email(message="Invalid email address.")])
    password = PasswordField(label='Password', validators=[DataRequired(),Length(min=8,max=30,message="Field must be at least 8 character long.")])
    submit = SubmitField(label="Log in")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/',methods=['GET','POST'])
def login():
    my_form = LoginForm()
    my_form.validate_on_submit()
    return render_template('login.html',form=my_form)

if __name__ == '__main__':
    app.config['SECRET_KEY'] = "hola"
    app.run(debug=True)