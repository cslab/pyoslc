from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SpecificationForm(FlaskForm):
    specification_id = StringField(validators=[DataRequired()])
    title = StringField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired()])
    author = StringField(validators=[DataRequired()])
    product = StringField(validators=[DataRequired()])
    subject = StringField(validators=[DataRequired()])
    source = StringField(validators=[DataRequired()])
    category = StringField(validators=[DataRequired()])
    submit = SubmitField("Save")


class SelectSpecificationForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    submit = SubmitField("Search")