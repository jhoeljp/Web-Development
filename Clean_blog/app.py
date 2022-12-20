#Flask modules
from flask import Flask, url_for
from flask import render_template,redirect

#API modules
import requests 
import json 

app = Flask(__name__)

@app.route('/')
def hello():
    data = api()
    return render_template("index.html",all_posts=data)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/post/<int:post_id>')
def post(post_id):
    data = api()[post_id-1]
    return render_template('post.html',post=data)

def api():
    endpoint ="https://api.npoint.io/c790b4d5cab58020d391"
    response = requests.get(url=endpoint)
    data = response.json()
    return data

if __name__ == "__main__":
    app.run(debug=True)