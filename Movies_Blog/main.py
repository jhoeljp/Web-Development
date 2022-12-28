from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import sqlite3

from os.path import exists
from os import getcwd

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


DB_NAME = "Movies"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}.db"
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(250),nullable=False)
    rating = db.Column(db.Float,nullable=False)
    ranking = db.Column(db.Integer,nullable=False)
    review = db.Column(db.String(250),nullable=False)
    img_url = db.Column(db.String(250),nullable=False)


class RateMovieForm(FlaskForm):
    rating = FloatField(label='Your Rating out of 10 eg: 7.5',validators=[DataRequired()])
    review = StringField(label = "Your review",validators=[DataRequired()])
    submit = SubmitField(label='Submit')

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

@app.route('/edit/<int:row_id>',methods=['GET','POST'])
def edit(row_id):
    edit_form = RateMovieForm()

    #get hold of movie on db
    

    if edit_form.validate_on_submit():
        #update records 
        with app.app_context():
            movie_query = db.session.query(Movie).filter_by(id=row_id).first()

            movie_query.rating = float(edit_form.rating.data)
            movie_query.review = str(edit_form.review.data)

            db.session.commit()

            return redirect(url_for('home'))

    else:
        row = {} 
        with app.app_context():
            movie_query = db.session.query(Movie).filter_by(id=row_id).first()
            row = movie_query
        return render_template('edit.html',form=edit_form,movie=row)

if __name__ == '__main__':
    app.run(debug=True)
