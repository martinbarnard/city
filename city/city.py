# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, render_template, request, flash, g, redirect, url_for)
import os
from .scraper import souper

app = Flask(__name__)

def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected variable {} unset".format(name)
        return ''
        #raise Exception(message)

app.config.from_object(__name__)
app.config.update(
    DB_URL='sqlite://city.db',
    SQLALCHEMY_DATABASE_URI = 'sqlite://app.db'
    PG_URL = get_env_var("POSTGRES_URL")
    PG_USER = get_env_var("POSTGRES_USER")
    PG_PW = get_env_var("POSTGRES_PW")
    PG_DB = get_env_var("POSTGRES_DB")
)

# These will bork if we don't have them

# A list of words to use for storing n stuff
our_words = [] 

# TODO: Fix URL
#DB_URL='postgresql::/{user}:{pw}@{url}/{db}'.format(user=PG_USER, pw=PG_PW, url=PG_URL, db=PG_DB)

db = SQLAlchemy(app)

################################################################################
# DB models
class Url(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(1024), unique = False, nullable = False)

class Words(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    word = db.Column(db.String(25), unique = False, nullable = False)
################################################################################

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

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
    myurl = request.form['url']
    db.urls.add(myurl)
    db.urls.commit()

    flash('inserted url')
    soup = souper(url)
    # Now we have stuff. let's do thing with it
    soup.get_url()
    soup.extract_stuff()
    soup.logic_up()
    common = soup.lemms_fdist.most_common(10)
    # Insert our common or even all data
    return str(common)
#    return redirect(url_for('get_by_id', url_id=1))
    
@app.route('/url_id/<int:url_id>')
def get_by_id(url_id):
    '''
    Will return the words
    '''
    print('url_id',url_id)
    return "hi there"

if __name__ == '__main__':
    print('starting up...')
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    app.run()
