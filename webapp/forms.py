from wtforms import Form, TextField, validators, StringField, SubmitField, fields, FormField
from wtforms.validators import Optional
from models import input_data, input_data1

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
