from time import time, sleep
from enum import Enum
from sqlalchemy import update
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, flash, request, url_for, jsonify, session, redirect, send_file
from wtforms import Form, TextField, validators, StringField, SubmitField, fields, FormField
from wtforms.validators import Optional
from celery import Celery
import matplotlib.pyplot as plt
import io
import http
import numpy as np
import redis

from helper import *

# How to start workers
# celery -A app.celery worker --loglevel=info


import sys
sys.path.append('/mnt/c/peter_abaqus/Summer-Research-Project/')
from my_meep.main import wsl_main
from my_meep.configs import config

# App config.
DEBUG = True
app = Flask(__name__)

# app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/2'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/2'

app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])


@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        print(name)

    if form.validate():
        # Save the comment here.
        #load the model and create script
        message = 'long_task peter'
        flash(message)
    else:
        flash('Error: All the form fields are required. ')

    return render_template('index.jinja', form=form)


@celery.task(bind=True)
def long_task(self, sections):
    _config = create_configs(sections, config=config)
    message = ''
    for i, total, res in wsl_main(web_config=_config):
        i = int(i+1)
        total = int(total)
        if not message:
            message = str(res)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})

    # total = np.random.randint(10, 50)
    # for i in range(total):
    #     if not message or np.random.random() < 0.25:
    #         message = 'hi'
    #     self.update_state(state='PROGRESS',
    #                       meta={'current': i, 'total': total,
    #                             'status': message})
    #     sleep(0.2)


    return {'current': i, 'total': total, 'status': 'Task completed!',
            'result': 42}

@app.route('/longtask', methods=['POST'])
def longtask():
    sections = ['Visualization', 'General',
                'Geometry', 'Simulation', 'Source']

    task = long_task.apply_async(kwargs={'sections': sections})
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/cakes')
def cakes():
    return render_template('nav.html')


@app.route('/home')
def home():
    return render_template('home.html')


# make models
# range inputs
class input_data(db.Model):
    __tablename__ = 'entry3'
    id = db.Column(db.Integer(), primary_key=True)
    spec = db.Column(db.String(50))
    start = db.Column(db.Float())
    stop = db.Column(db.Float())
    steps = db.Column(db.Float())
    input_data_id = db.Column(
        db.Integer(), db.ForeignKey('input_data_list.id'))

# single input


class input_data1(db.Model):
    __tablename__ = 'entry1'
    id = db.Column(db.Integer(), primary_key=True)
    spec = db.Column(db.String(50))
    val = db.Column(db.Float())
    input_data_id = db.Column(
        db.Integer(), db.ForeignKey('input_data_list.id'))


# radio
class derive_enum(Enum):
    def __str__(self):
        return str(self.value)

    def __iter__(self):
        return ((x.name, x.value) for x in Enum(self).__iter__())


class radio_data(db.Model):
    __tablename__ = 'radio'
    id = db.Column(db.Integer(), primary_key=True)
    spec = db.Column(db.String(50))
    default = db.Column(db.String(50))
    # choices = db.Column(db.Array(db.String, dimensions=2))
    input_data_id = db.Column(
        db.Integer(), db.ForeignKey('radio_check_data_list.id'))


class check_data(radio_data):
    __tablename__ = 'check'


class input_data_list(db.Model):
    __tablename__ = 'input_data_list'
    id = db.Column(db.Integer(), primary_key=True)
    section = db.Column(db.String(50))

    values = db.relationship('input_data')
    values1 = db.relationship('input_data1')


class radio_check_data_list(db.Model):
    __tablename__ = 'radio_check_data_list'
    id = db.Column(db.Integer(), primary_key=True)

    section = db.Column(db.String(50))

    radio = db.relationship('radio_data')
    check = db.relationship('check_data')


class input_form(Form):
    spec = TextField()
    start = fields.FloatField(validators=[Optional()])
    stop = fields.FloatField()
    steps = fields.FloatField()


class input_form1(Form):
    spec = TextField()
    val = fields.FloatField(validators=[Optional()])


class radio_form(Form):
    spec = TextField()
    val = fields.RadioField()


class input_form_list(Form):
    """A form for one or more addresses"""
    values = fields.FieldList(
        FormField(input_form, default=lambda: input_data()), min_entries=0)
    values1 = fields.FieldList(
        FormField(input_form1, default=lambda: input_data1()), min_entries=0)


def create_configs(sections, config):
    for s in sections:
        _input_data_list = input_data_list.query.filter_by(section=s).first()
        _radio_check_data_list = radio_check_data_list.query.filter_by(
            section=s).first()

        sections_code_web = ['Visualization', 'General',
                             'Geometry', 'Simulation', 'Source']
        sections_code_config = ['visualization',
                                'general', 'geo', 'sim', 'source']
        index = sections_code_web.index(s)
        s = sections_code_config[index]

        for v in _input_data_list.values:
            config.set(s, v.spec, ', '.join(
                [str(v.start), str(v.stop), str(v.steps)]))
        for v in _input_data_list.values1:
            config.set(s, v.spec, str(v.val))
        for v in _radio_check_data_list.radio:
            config.set(s, v.spec, v.default)
        for v in _radio_check_data_list.check:
            config.set(s, v.spec, v.default)

    return config


def process(section,  _fields):
    _input_data_list = input_data_list.query.filter_by(section=section).first()
    _radio_check_data_list = radio_check_data_list.query.filter_by(
        section=section).first()

    if len(_input_data_list.values) == 0:
        for key, val in _fields['input_range'].items():
            _input_data_list.values.append(input_data(
                spec=key, start=val[0], stop=val[1], steps=val[2]))
        for key, val in _fields['input'].items():
            _input_data_list.values1.append(input_data1(spec=key, val=val))
        for key, val in _fields['radio'].items():
            _radio_check_data_list.radio.append(
                radio_data(spec=key, default=val[0]))
        for key, val in _fields['check'].items():
            _radio_check_data_list.check.append(
                check_data(spec=key, default=val[0]))

    form = input_form_list(request.form, obj=_input_data_list)
    form.active = section

    radio_list = []

    if request.method != 'POST':
        for i, iter in enumerate(_fields['radio'].items()):
            key, val = iter

            class f(Form):
                name = key
            setattr(f, key, fields.RadioField(
                label=key, default=_radio_check_data_list.radio[i].default, choices=val[1], _name=key))
            f_obj = f()

            # f_obj.a.default = val[0]
            # f_obj.__init__()
            radio_list.append(f_obj)
    elif form.validate():
        for i, iter in enumerate(_fields['radio'].items()):
            key, val = iter

            class f(Form):
                name = key
            setattr(f, key, fields.RadioField(
                label=key, default=request.form[key], choices=val[1], _name=key))
            f_obj = f()

            # f_obj.a.default = val[0]
            # f_obj.__init__()
            radio_list.append(f_obj)

    if request.method == 'POST' and form.validate():
        for i, d in enumerate(_radio_check_data_list.radio):
            _radio_check_data_list.radio[i].default = request.form[_radio_check_data_list.radio[i].spec]

        form.populate_obj(_input_data_list)

        db.session.commit()

        # print('form is: ')
        # for key in form:
        #     print(key)

        # print('Val form is:')
        # for key in request.form:
        #     print(key, request.form[key])

        # print(_input_data_list.values[0].start)
        # flash("Saved Changes")

    elif request.method == 'POST':
        print('error is', form.errors)
        # print('Val form is:')
        # for key in request.form:
        #     print(key, request.form[key])

    #     for k in request.form['radio-0']:
    #         print('error', k)

    if request.method == 'POST' and form.validate() and request.form['action'] == 'Simulate':
        return ('', http.HTTPStatus.NO_CONTENT)

    return render_template('features.html', title=section,  form=form, radio_list=radio_list)


@app.route('/visualization', methods=['GET', 'POST'])
def login():

    info = {
        'check': {
        },
        'radio': {
            'structure':  ('False', ('True', 'False')),
            'transiant':  ('False', ('True', 'False')),
            'rms':  ('True', ('True', 'False')),
            'view_only_particles':  ('True', ('True', 'False')),
            'log_res':  ('False', ('True', 'False')),
        },
        'input_range': {
            'viz_offset':  [0, 0, 0]
        },
        'input': {
            '3d_plotting_axis':  1,
            'frame_speed':  200,

        }
    }
    return process('Visualization', info)


@app.route('/geometry', methods=['GET', 'POST'])
def a2():
    info = {
        'check': {

        },
        'radio': {
            # 'shape_types_dummy': ('cube', ('sphere', 'triangle', 'hexagon', 'cube'))
        },
        'input_range': {
            'particle_size': [0.05, 0.12, 1],
            'x_loc': [0, -3.4, 1],
            'distance': [1, 3, 1],
            'fill_factor': [0.5, 0.7, 1],
            'std': [0.1, 0.3, 1],

            'solid_center': [-2, 0, 0],
            'cell_size':  [10, 10, 10],
            'rotation': [0, 60, 1]
        },
        'input': {
            'pml_thick': 0.5,
            'num_particles': 2,
        }
    }

    f, radio_list = process('Geometry', info)
    return render_template('features.html', title='Geometry',  form=f, radio_list=radio_list)


@app.route('/simulation', methods=['GET', 'POST'])
def a3():
    info = {
        'check': {

        },
        'radio': {
            'sim':  ('checker', ('checker', 'simple shape', 'voronoi'))
        },
        'input_range': {

        },
        'input': {
            'dimension':  2,
            'resolution':  60,
            'change_res':  1,
            'time':  1000,
            'out_every':  0.2,
            'save_every':  30
        }
    }

    f, radio_list = process('Simulation', info)
    return render_template('features.html', title='Simulation',  form=f, radio_list=radio_list)


@app.route('/general', methods=['GET', 'POST'])
def a4():
    info = {
        'check': {

        },
        'radio': {
            'verbals':  ('True', ('True', 'False')),
            'gen vor':  ('False', ('True', 'False')),
            'meep sim':  ('True', ('True', 'False')),
            'gen gmsh':  ('False', ('True', 'False')),
            'process inp':  ('False', ('True', 'False')),
            'clean array':  ('False', ('True', 'False')),
            'sim abq':  ('True', ('True', 'False')),
        },
        'input_range': {

        },
        'input': {

        }
    }

    f, radio_list = process('General',  info)
    return render_template('features.html', title='General',  form=f, radio_list=radio_list)


@app.route('/source', methods=['GET', 'POST'])
def a5():
    info = {
        'check': {
        },
        'radio': {
            'mode':  ('normal', ('normal', 'gaussian', 'far_field_transform', 'waveguide')),

        },
        "input_range": {
            'size':  [0, 10, 0],
            'center':  [4, 0, 0],
            'near_flux_loc':  [3.5, 0, 0],
            'far_flux_loc':  [-4.5, 0, 0],
            'flux_size':  [0, 9, 0],

        },
        'input': {
            'fcen':  0.8167,
            'tilt_angle':  0,
            'sigma':  2,
            'amp':  100,
            'flux_nfreq':  100,
            'fwidth':  2,
            'flux_width':  0.8,

        }
    }

    f, radio_list = process('Source', info)
    return render_template('features.html', title='Source',  form=f, radio_list=radio_list)


@app.route('/pricing', methods=['GET', 'POST'])
def pricing():
    return render_template('pricing.html')
    


@app.route('/sim_image_data', methods=['GET'])
def correlation_matrix():
    # a = [1,2,3]
    # b = [4,5,6]
    # plt.plot(a, b)
    # bytes_image = io.BytesIO()
    # plt.savefig(bytes_image, format='png')
    # bytes_image.seek(0)
    # return bytes_image

    # bytes_obj = get_correlation_matrix_as_bytes()

    r = redis.Redis(host = 'localhost', port = 6379, db=0)
    bytes_obj = io.BytesIO(r.get('RMS image'))
    print('read figure')
    bytes_obj.seek(0)
    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')
  

# - - - Execute - - -
def prep_db():
    db.drop_all()
    db.create_all()
    sections = ['Visualization', 'General', 'Geometry', 'Simulation', 'Source']
    for s in sections:
        _input_data_list = input_data_list(section=s)
        _radio_check_data_list = radio_check_data_list(section=s)
        db.session.add(_input_data_list)
        db.session.add(_radio_check_data_list)
    db.session.commit()


if __name__ == '__main__':
    prep_db()
    app.run(debug=True, host='0.0.0.0')
