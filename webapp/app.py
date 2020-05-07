from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from celery import Celery
from script import wrap_script, RNN

# App config.
DEBUG = True
app = Flask(__name__)
app1 = Celery('hello', broker='amqp://guest@localhost//')

app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    
    @app.route("/", methods=['GET', 'POST'])
    def index():
        form = ReusableForm(request.form)

        print (form.errors)
        if request.method == 'POST':
            name=request.form['name']
            print (name)
        
        if form.validate():
        # Save the comment here.
            #load the model and create script
            message = hello(name) 
            flash(message)
        else:  
            flash('Error: All the form fields are required. ')
        
        return render_template('index.html', form=form)

@app1.task
def hello(name):
    return wrap_script(name)

@app.route('/cakes')
def cakes():
    return render_template('cake.html')

     
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')