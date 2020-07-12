# App config.

from flask import Flask
from dynamic_plot import plot_page

DEBUG = True
app = Flask(__name__)
app.register_blueprint(plot_page)

app.config.from_pyfile('app.cfg')
