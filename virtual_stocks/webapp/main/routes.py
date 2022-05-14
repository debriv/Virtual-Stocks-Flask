from flask import   (render_template,
                    url_for, 
                    flash, 
                    redirect, 
                    request , 
                    abort,
                    Blueprint)

from webapp.main.forms import SearchForm
from webapp.main.utils import search_key


main = Blueprint('main',__name__)

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect((url_for('main.search_results', query=form.search.data)))
    return render_template('home.html', form=form)#, posts=posts)

@main.route('/search_results/<query>')
def search_results(query):
  results = search_key(query)
  return render_template('search_results.html', results=results)

@main.route("/about")
def about():
    return render_template('about.html', title ='About')