from flask import Blueprint, render_template

from app.models import EditableHTML, UsefulLink

main = Blueprint('main', __name__)


@main.route('/')
def index():
    useful_links = UsefulLink.query.all()
    return render_template('main/index.html',
        useful_links=useful_links
    	)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', 
        editable_html_obj=editable_html_obj
        )
