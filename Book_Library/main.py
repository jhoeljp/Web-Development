from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os.path import exists
from os import getcwd


app = Flask(__name__)

all_books = []

DB_NAME = "book-collection"
#SQLAlchemy database 
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250),nullable=False)
    author = db.Column(db.String(250),nullable=False)
    rating = db.Column(db.Float,nullable=False)

#create database if file missing 
db_path = f"{str(getcwd())}\\instance\\{DB_NAME}"

if not exists(db_path):
    with app.app_context():
        #create data base table
        db.create_all()
        db.session.commit()

@app.route('/')
def home():

    #request all books on data base 
    with app.app_context():
        all_books = db.session.query(Books).all()
        db.session.close()

    return render_template('index.html',book_list=all_books)


@app.route("/add",methods=['GET','POST'])
def add():

    if request.method == 'GET':
        return render_template('add.html')

    else:
        #add data to List
        new_book = {
        "title": request.form['title'],
        "author": request.form['author'],
        "rating": request.form['rating'],
        }

        #add new book to database 
        with app.app_context():
            book = Books(title=new_book['title'],
                        author=new_book['author'],
                        rating=new_book['rating'])
            db.session.add(book)
            db.session.commit()
            db.session.close()

        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

