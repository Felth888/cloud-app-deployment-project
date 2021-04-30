from flask_wtf import FlaskForm
from wtforms.fields.html5 import IntegerField, DateField
from wtforms.fields import SubmitField, StringField, RadioField, BooleanField, \
                            HiddenField
from wtforms.validators import DataRequired, NumberRange, optional
from datetime import date, datetime

def validate_beaten(form, self):
    if form.beaten.data is not None:
        if form.beaten.data > date.today():
            raise ValueError("date can't be after today")
        if form.completed.data is not None and \
           form.beaten.data > form.completed.data:
            raise ValueError("Date can't be after date completed")

def validate_completed(form, self):
    if form.completed.data is not None:
        if form.completed.data > date.today():
            raise ValueError("date can't be after today")

def validate_added(form, self):
    if form.added.data > date.today():
        raise ValueError("Date can't be after today")
    if form.completed.data is not None:
        if form.completed.data > form.added.data:
            raise ValueError("Date can't be after date added")
    if form.beaten.data is not None:
        if form.beaten.data > form.added.data:
            raise ValueError("Date can't be after date added")



class UpdateGame(FlaskForm):
    """Update existing game form"""

    progress = IntegerField('Progress',
        [NumberRange(min=0, max=100, message="Value must be between 0 and 100")],)

    status = RadioField('Status*', choices=[('Unplayed', 'Unplayed'),
                                            ('Unfinished','Unfinished'),
                                            ('Beaten','Beaten'),
                                            ('Completed','Completed'),
                                            ('Abandoned','Abandoned')],)

    playing = BooleanField('Playing Now')

    beaten = DateField('Date Beaten',[optional(), validate_beaten])

    completed = DateField('Date Completed',[optional(), validate_completed])

    submit = SubmitField('Submit')

class NewGame(FlaskForm):
    """Add new game form."""

    title = StringField('Name*', [DataRequired(message="Title Required")])

    platform = StringField('Platform*', [DataRequired(message="Platform Required")])

    genre = StringField('Genre*', [DataRequired(message="Genre Required")])

    progress = IntegerField('Progress',
            [NumberRange(min=0, max=100, message="Value must be between 0 and 100")],
            default=0)

    status = RadioField('Status*', choices=[('Unplayed', 'Unplayed'),
                                            ('Unfinished','Unfinished'),
                                            ('Beaten','Beaten'),
                                            ('Completed','Completed'),
                                            ('Abandoned','Abandoned')],
                                    default='Unplayed')

    playing = BooleanField('Playing Now', default=False)

    added = DateField('Date Added', [validate_added], default=date.today())

    beaten = DateField('Date Beaten', [optional(), validate_beaten])

    completed = DateField('Date Completed', [optional(), validate_completed])

    submit = SubmitField('Submit')


