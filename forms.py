from datetime import date, timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from wtforms.validators import Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Admin')
    submit = SubmitField('Register')


class IndexForm(FlaskForm):
    submit = SubmitField('Show list')


class FilterForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', render_kw={"placeholder": "YYYY-MM-DD"},
                           validators=[Optional()], default=(date.today() - timedelta(days=90)))
    end_date = DateField('End Date', format='%Y-%m-%d', render_kw={"placeholder": "YYYY-MM-DD"},
                         validators=[Optional()], default=date.today)
    calling_id = IntegerField('Calling ID', render_kw={"placeholder": "Enter Calling ID"},
                              validators=[Optional(), NumberRange(min=1, max=999)])
    called_id = IntegerField('Called ID', render_kw={"placeholder": "Enter Called ID"},
                             validators=[Optional(), NumberRange(min=800, max=999)])
    site = SelectField(
        'Site',
        choices=[('all', 'ALL'), (1, 1), (2, 2), (3, 3)],
        validators=[Optional()]
    )
    submit = SubmitField('Apply Filter')
    export = SubmitField('Export data')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
