from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, validators)
from wtforms.validators import InputRequired, Length
class MedicineForm(FlaskForm):
    medicine_name = StringField('medicine_name', [validators.Length(min=1, max=50)])
    how_to_use = TextAreaField('How to use',[validators.InputRequired(), validators.Length(max=500)])
    price = IntegerField('Price', [validators.InputRequired()])