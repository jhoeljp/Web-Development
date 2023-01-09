from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'

#database cpmfig params
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#downloadable files path 
app.config['UPLOAD_FOLDER'] = 'static/files/'

#configuring login manager for flask login
login_manager = LoginManager(app)

db = SQLAlchemy(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


#callback to refresh user id 
@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.query(User).filter_by(id=user_id).first_or_404()

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=['GET','POST'])
def register():

    if request.method=='GET':
        return render_template("register.html")
    else:
        #store form info 
        name = request.form['name']
        email = request.form['email']

        #encrypt password with sha256 and salt round of length 8 
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)

        #create db object 
        new_user = User(name=name,email=email,password=password)

        with app.app_context():
            #send to db 
            db.session.add(new_user)
            #save on db 
            db.session.commit()

            db.session.close()

            #send name to secrets 
            return redirect(url_for('home'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        
        #find user on database 
        with app.app_context():

            user = db.session.query(User).filter_by(email=email).first()
            
            matched_password = check_password_hash(user.password,password)

            db.session.close()

            if matched_password:

                #login user 
                login_user(user)

                return redirect(url_for('secrets'))

    return render_template("login.html")

@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    filename = "cheat_sheet.pdf"
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
