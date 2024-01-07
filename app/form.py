from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, RadioField, validators, DateTimeField,SubmitField
from wtforms.validators import InputRequired, Length, DataRequired
class MedicineForm(FlaskForm):
    medicine_name = StringField('medicine_name', [validators.Length(min=1, max=50)])
    how_to_use = TextAreaField('How to use',[validators.InputRequired(), validators.Length(max=500)])
    price = IntegerField('Price', [validators.InputRequired()])

class PatientForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired()])
    gender = RadioField('Giới tính', choices=[('nam', 'Nam'), ('nữ', 'Nữ')], default='nam')
    date_appointment = DateTimeField('Ngày hẹn khám', validators=[DataRequired()])
    date_of_birth = DateTimeField('Ngày sinh', validators=[DataRequired()])
    address = StringField('Địa chỉ', validators=[DataRequired()])
    disease_history = StringField('Lịch sử bệnh')
    submit = SubmitField('Submit')