from flask import Flask, render_template, redirect, url_for, flash,jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps 

#init flask app 
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

#init CKEditor for blog post and comments
ckeditor = CKEditor(app)

#init Bootstrap for styling 
Bootstrap(app)

#Connect flask app to local db 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#init sql alchemy for sql queries
db = SQLAlchemy(app)
db.session.expire_on_commit = False

#init gravatar for comments section avatars
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

##CONFIGURE TABLES
class Users(db.Model, UserMixin):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)

    #One to Many relationship with BlogPost
    posts = relationship("BlogPost", back_populates="author")

    #One to Many relationship wiht Users
    comments = relationship('Comment',back_populates='author')


class BlogPost(db.Model):

    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    #Many to One relationship with Users
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    author = relationship("Users", back_populates="posts")

    #One to Many relationship with Comments
    comments = relationship('Comment',back_populates='blog_post')

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text,nullable=False)

    #Many to One relationship with User
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    author = relationship("Users",back_populates='comments')

    #Many to One relationship with BlogPost
    blog_post_id = db.Column(db.Integer,db.ForeignKey('blog_posts.id'))
    blog_post = relationship('BlogPost',back_populates='comments')

#create database tables 
# with app.app_context():
#     db.create_all()

#LOGIN MANAGER INIT
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = None
    with app.app_context():
        user = db.session.query(Users).filter_by(id=user_id).first()
        db.session.close()
    return user

#ADMIN ONLY DECORATOR 
@app.errorhandler(403)
def admin_only(f):
    @wraps(f)
    def wrapper():
        if current_user.get_id() != '1':
            return render_template('403.html'), 403
        else:
            return f()
    return wrapper

#FLASK APP ROUTES

@app.route('/')
def get_all_posts():
    posts = []
    try:
        # with app.app_context():
        posts = db.session.query(BlogPost).all()
            # db.session.close()
    except:
        pass
    return render_template("index.html", all_posts=posts)


@app.route('/register',methods=["GET","POST"])
def register():
    error= None
    form = RegisterForm()

    if form.validate_on_submit():
        
        #create new user 
        try:
            with app.app_context():

                new_user = Users(name = form.name.data, 
                                email=form.email.data,
                                password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8))

                #store new user on data base table Users
                db.session.add(new_user)

                db.session.commit()

                #automatically log in new user 
                login_user(new_user)
                
                flash('Logged in successfully.')

                #close db session 
                db.session.close()

                return redirect(url_for('get_all_posts'))

        except Exception as ex:

            flash('You have already registered with that email. log in instead !"')
            return redirect(url_for('login'))

    return render_template("register.html",form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            #check input with Users Table 
            with app.app_context():

                email = form.email.data

                user = db.session.query(Users).filter_by(email=email).first()

                db.session.close()

                #check if correct password
                matched_password = check_password_hash(user.password,form.password.data)

                if matched_password:

                    # Login and validate the user.

                    login_user(user)

                    return redirect(url_for('get_all_posts'))
                else:
                    flash("Incorrect Password, please try again !")
                    return redirect(url_for('login'))
        except:
            flash("Incorrect Email, please try again !")
            return redirect(url_for('login'))
                

    return render_template("login.html",form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>",methods=['GET','POST'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():

        #check if user is logged in 
        if current_user.is_authenticated:
            #create and commit comment to db 
            new_comment = Comment(
                text=comment_form.body.data,
                author = current_user,
                blog_post = requested_post
            )

            db.session.add(new_comment)
            db.session.commit()

        #user not authenticated 
        else:
            flash('login is required for leaving a comment! ')
            return redirect(url_for('login'))
    post_comments = db.session.query(Comment).filter_by(blog_post_id=post_id).all()
    return render_template("post.html", post=requested_post,comment=comment_form,all_comments = post_comments)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/new-post",methods=['GET','POST'])
@admin_only
def add_new_post():

    form = CreatePostForm()

    if form.validate_on_submit():

        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        with app.app_context():
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>",methods=['GET','POST'])
def edit_post(post_id):

    with app.app_context():
        # post = BlogPost.query.get(post_id)
        post = db.session.query(BlogPost).filter_by(id=post_id).first()

        edit_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            body=post.body
        )

        if edit_form.validate_on_submit():

            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.body = edit_form.body.data
                
            db.session.commit()

            return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
