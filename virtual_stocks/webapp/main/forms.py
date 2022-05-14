from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class SearchForm(FlaskForm):
  search = StringField('search', [DataRequired()])
  submit = SubmitField('Search',
                       render_kw={'class': 'btn btn-lg btn-success'})