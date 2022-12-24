from flask import Flask, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key shhh'
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(),URL()])
    open = StringField('Opening time e.g.8AM', validators=[DataRequired()])
    close = StringField('Closing time e.g.5:30PM', validators=[DataRequired()])
    coffee_rating = SelectField(label='Coffee Rating', choices=['✘','☕️','☕️☕️','☕️☕️☕️','☕️☕️☕️☕️','☕️☕️☕️☕️☕️'])
    wifi_strength_rating = SelectField(label='Wifi Strength Rating', choices=['✘','💪','💪💪','💪💪💪','💪💪💪💪','💪💪💪💪💪💪'])
    power_socket_rating = SelectField(label='Power Socket Rating', choices=['✘','🔌','🔌🔌','🔌🔌🔌','🔌🔌🔌🔌','🔌🔌🔌🔌🔌'])
    
    submit = SubmitField('Submit')

# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add',methods=['GET','POST'])
def add_cafe():

    form = CafeForm()
    
    if form.validate_on_submit():

        new_cafe = []
        new_cafe.append(form.cafe.data)
        new_cafe.append(form.location.data)
        new_cafe.append(form.open.data)
        new_cafe.append(form.close.data)

        new_cafe.append(form.coffee_rating.data)
        new_cafe.append(form.wifi_strength_rating.data)
        new_cafe.append(form.power_socket_rating.data)

        #write new row of info to csv file 
        with open('cafe-data.csv','a', encoding="utf8") as csv_file:

            writer_obj = csv.writer(csv_file)
            writer_obj.writerow(new_cafe)

            csv_file.close()
        
        #redirect to lits of cafes
        return redirect('cafes')

    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', encoding="utf8", newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
