from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

from datetime import date


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret707'
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body= CKEditorField('Body',validators=[DataRequired()])
    submit = SubmitField("Submit Post")

@app.route('/')
def get_all_posts():

    posts = None

    #fetch from database 
    with app.app_context():

        posts = db.session.query(BlogPost).all()
        db.session.close()

    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):

    requested_post = None

    #fetch from database 
    with app.app_context():

        #fetch post with id 
        requested_post = db.session.query(BlogPost).filter_by(id=post_id).first()
        db.session.close()
        
        #render post           
        return render_template("post.html", post=requested_post)

@app.route('/new-post', methods=['GET','POST'])
def new_post():
    #create new make post form 
    new_form = CreatePostForm()

    #method == 'POST'
    if new_form.validate_on_submit():
        #update database with new post info 
        with app.app_context():
            
            #get date published 
            today = date.today()
            #format date as August 31, 2019
            todays_date = f"{today.month} {today.day}, {today.year}"

            #make new blog post Object with "post" form 
            new_blog_post = BlogPost(title=new_form.title.data,
                                    subtitle=new_form.subtitle.data,
                                    date=todays_date,
                                    body=new_form.body.data,
                                    author=new_form.author.data,
                                    img_url=new_form.img_url.data)

            #add and commit changes to database
            db.session.add(new_blog_post)
            db.session.commit()

            # db.session.close()

            #finally redirect home 
            return redirect(url_for('get_all_posts'))

    #method == 'GET'
    else:
        #header background image
        style = url_for('static', filename='img/edit-bg.jpg')

        #render make post html 
        return render_template('make-post.html',header_title="New Post",make_post_form=new_form,header_style=style)

@app.route('/edit-post/<int:post_id>',methods=['GET','POST'])
def edit_post(post_id):

    #create new make post form 
    new_form = CreatePostForm()

    #When edit post form gets submitted 
    if new_form.validate_on_submit():

        #update edited post on databse 
        with app.app_context():
            #filter by unique field title 
            post = db.session.query(BlogPost).filter_by(id=post_id).first()
            
            #Update database info
            #date field stays the same

            post.title = new_form.title.data
            post.subtitle = new_form.subtitle.data
            post.author = new_form.author.data
            post.body = new_form.body.data
            post.img_url = new_form.img_url.data

            db.session.commit()
            db.session.close()

            #redirect user to post.html 
            return redirect(url_for('show_post',post_id=post_id))
    else:
        with app.app_context():

            #fetch post from database
            edit_post = db.session.query(BlogPost).filter_by(id=post_id).first()

            db.session.close()

            #pre-fill form with info from database
            new_form.title.data = edit_post.title
            new_form.subtitle.data = edit_post.subtitle
            new_form.author.data = edit_post.author
            new_form.img_url.data= edit_post.img_url
            new_form.body.data = edit_post.body

            #header background image
            style = url_for('static', filename='img/edit-bg.jpg')
            
            return render_template('make-post.html',header_title="Edit Post",make_post_form=new_form,header_style=style)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)