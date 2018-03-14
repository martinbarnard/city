# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, render_template, request, flash, g, redirect, url_for)
#from werkzeug import SharedDataMiddleware
import os
from .scraper import souper

def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected variable {} unset".format(name)
        raise Exception(message)

# These will bork if we don't have them
#POSTGRES_URL = get_env_var("POSTGRES_URL")
#POSTGRES_USER = get_env_var("POSTGRES_USER")
#POSTGRES_PW = get_env_var("POSTGRES_PW")
#POSTGRES_DB = get_env_var("POSTGRES_DB")

our_words = [] # A list of words to use for storing n stuff

# TODO: Fix URL
#DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
DB_URL=''
app = Flask(__name__)
db = SQLAlchemy(app)

class Url(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(1024), unique = False, nullable = False)

# Will store the links to our words
class Words(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    word = db.Column(db.String(25), unique = False, nullable = False)

@app.cli.command('createdb')
def createdb_command():
    '''
    Create our db & tables
    '''
    from sqlalchemy_utils import database_exists, create_database
    if not database_exists(DB_URL):
        print('creating db')
        create_database(DB_URL)
    print('creating tables')
    db.create_all()
    print('done')

@app.route('/')
def index():
    '''
    Will take a url and parse the fucker
    TODO: get url from get args
    '''
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_url():
    url = request.form['url']
    soup = souper(url)
    # Now we have stuff. let's do thing with it
    soup.get_url()
    soup.extract_stuff()
    soup.logic_up()
    common = soup.lemms_fdist.most_common(10)
    return redirect(url_for('get_by_id'))
    
@app.route('/url_id/<int:url_id>')
def get_by_id(url_id):
    '''
    Will return the words
    '''

if __name__ == '__main__':
    print('starting up...')
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    app.run()
