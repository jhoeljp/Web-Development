#Flask modules
from flask import Flask
from flask import render_template,request

#API modules
import requests 
import json 

#SMTP 
import smtplib
from dotenv import load_dotenv
from os import getcwd, environ
import ssl


app = Flask(__name__)

@app.route('/')
def hello():
    data = api()
    return render_template("index.html",all_posts=data)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact',methods=['GET','POST'])
def contact():
    title = ""
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        #send email using smtp
        try:
            send_email_smtp(name,email,phone,message)

            title = "Successfully sent your message"
        except: 
            title = "Error sending your message"
    else:
        title = "Contact Me"
    return render_template("contact.html",message=title)

@app.route('/post/<int:post_id>')
def post(post_id):
    data = api()[post_id-1]
    return render_template('post.html',post=data)

def api():
    endpoint ="https://api.npoint.io/c790b4d5cab58020d391"
    response = requests.get(url=endpoint)
    data = response.json()
    return data

def send_email_smtp(name,email,phone,msg):
    #get environment path 
    env_path = f"{getcwd()}\secrets.env"
    print(env_path)

    load_dotenv(env_path)

    #load email variables for smtp 
    EMAIL_USER = environ.get("EMAIL")
    PASSWORD = environ.get("PASSWORD")
    EMAIL_SERVER = environ.get("EMAIL_SERVER")

    #port for gmail 
    ssl_port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(EMAIL_SERVER,ssl_port,context=context) as connection:
        try:     
            #login with internal email details 
            connection.login(user=EMAIL_USER,password=PASSWORD)
            
            message = f"""
                    Name:{name}
                    Email:{email}
                    Phone:{phone}
                    Message:{msg}
                    """
            
            #send email message 
            connection.sendmail(msg=message, from_addr=EMAIL_USER, to_addrs=email)
            
        except smtplib.SMTPException as e :
            print("Email could not be sent! ")
            print(e)
            raise Exception
        finally: 
            connection.quit()

if __name__ == "__main__":
    app.run(debug=True)