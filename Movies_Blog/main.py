from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

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

with app.app_context():
    #create dabase if .db file not present 
    db_path = f"{getcwd()}\\instance\\{DB_NAME}"

    if not exists(db_path):
        db.create_all()

    new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )

    db.session.add(new_movie)
    db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
