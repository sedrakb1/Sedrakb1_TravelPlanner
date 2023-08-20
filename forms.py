from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class ItineraryForm(FlaskForm):
    day = StringField('Day', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
