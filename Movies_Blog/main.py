from flask import Flask, render_template, redirect, url_for

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired

import requests
from dotenv import load_dotenv
from os import environ

from os.path import exists
from os import getcwd

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


DB_NAME = "Movies"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}.db"
db = SQLAlchemy(app)

#databse schema
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(250),nullable=False)
    rating = db.Column(db.Float,nullable=False)
    ranking = db.Column(db.Integer,nullable=False)
    review = db.Column(db.String(250),nullable=False)
    img_url = db.Column(db.String(250),nullable=False)

#Update movie Form
class RateMovieForm(FlaskForm):
    rating = FloatField(label='Your Rating out of 10 eg: 7.5',validators=[DataRequired()])
    review = StringField(label = "Your review",validators=[DataRequired()])
    submit = SubmitField(label='Submit')

#Add Movie form 
class AddMovieForm(FlaskForm):
    title = StringField(label="Movie title",validators=[DataRequired()])
    add_movie = SubmitField(label="Add Movie")

#Fetch API key from secret file 
def get_TMDB_Key():
    secrets_path = f"{getcwd()}/secrets.env"

    API_KEY = ""

    if exists(secrets_path):
        load_dotenv(secrets_path)
        API_KEY = environ.get('KEY')
    
    else:
        msg = 'Missing TMDB API Key on secrets.env ! '
        print(msg)
        raise(msg)

    return API_KEY

#create dabase if .db file not present 
db_path = f"{getcwd()}\\instance\\{DB_NAME}.db"

if not exists(db_path):
    with app.app_context():
        db.create_all()
else:
    print(f"database {DB_NAME} already exists! ")

    # new_movie = Movie(
    #     title="2001 Space Odessey",
    #     year=1968,
    #     description="After discovering a monolith on the lunar surface, the Discovery One and its revolutionary supercomputer set out to unravel its mysterious origin.",
    #     rating=9.2,
    #     ranking=10,
    #     review="My favourite space movie.",
    #     img_url="https://miro.medium.com/max/840/1*oGtJQ6pcuEZMo9A1SEUAJA.jpeg"
    # )

    # db.session.add(new_movie)
    # db.session.commit()

@app.route("/")
def home():
    #request all records on db 
    movie_list = []

    with app.app_context():

        movie_list = db.session.query(Movie).all()
        db.session.close()

    return render_template("index.html",movies=movie_list)

@app.route('/add',methods=['GET','POST'])
def add():
    add_form = AddMovieForm()

    if add_form.validate_on_submit():
        #search movie db api for info on movie 
        API_KEY = get_TMDB_Key()
        if API_KEY=="":print("API_KEY Empty!!!!!! ")
        else:print(API_KEY)
        query = add_form.title.data

        end_point = "https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={query}&page=1&include_adult=false"

        response = requests.get(url=end_point).json()

        print(response)
        return redirect(url_for('home'))

    else:
        return render_template('add.html',form = add_form)


@app.route('/edit/<int:row_id>',methods=['GET','POST'])
def edit(row_id):

    #create edit form with quick forms
    edit_form = RateMovieForm()

    #on POST request
    if edit_form.validate_on_submit():

        #update records 
        with app.app_context():
            movie_query = db.session.query(Movie).filter_by(id=row_id).first()

            movie_query.rating = float(edit_form.rating.data)
            movie_query.review = str(edit_form.review.data)

            #save changes to db
            db.session.commit()

            return redirect(url_for('home'))

    else:
        row = {} 
        with app.app_context():

            #fetch row to be updated
            movie_query = db.session.query(Movie).filter_by(id=row_id).first()
            row = movie_query

        return render_template('edit.html',form=edit_form,movie=row)


@app.route('/delete/<int:row_id>')
def delete(row_id):

    with app.app_context():

        movie = db.session.query(Movie).filter_by(id=row_id).first()
        db.session.delete(movie)

        db.session.commit()

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
