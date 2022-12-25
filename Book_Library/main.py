from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

all_books = []


@app.route('/')
def home():
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

        all_books.append(new_book)

        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

