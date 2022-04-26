from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SpecificationForm(FlaskForm):
    specification_id = StringField(
        validators=[DataRequired()], render_kw={"class_": "form-control-sm"}
    )
    title = StringField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired()])
    author = StringField(validators=[DataRequired()])
    product = StringField(validators=[DataRequired()])
    subject = StringField(validators=[DataRequired()])
    source = StringField(validators=[DataRequired()])
    category = StringField(validators=[DataRequired()])


class SelectSpecificationForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    selection = SelectField(option_widget="size=10")
    submit = SubmitField("Search")
