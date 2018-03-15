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
    SQLALCHEMY_DATABASE_URI = 'mysql://citystasher:citycity@localhost/citystasher',
    PG_URL = get_env_var("POSTGRES_URL"),
    PG_USER = get_env_var("POSTGRES_USER"),
    PG_PW = get_env_var("POSTGRES_PW"),
    PG_DB = get_env_var("POSTGRES_DB"),
)

# These will bork if we don't have them
app.config['SECRET_KEY'] = 'thisisacrappykey'

# A list of words to use for storing n stuff
our_words = [] 
db = SQLAlchemy(app)

# Crappy migrations
try:
    db.create_all()
except Exception as e:
    print('cant create db', e)

################################################################################
# DB models
class Scraper(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(1024), unique = False, nullable = False)
    def __repr__(self):
        return '<Scraper {}>'.format(self.url)

class Words(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    word = db.Column(db.String(25), unique = False, nullable = False)
    wordcount = db.Column(db.Integer)
################################################################################


@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Scraper':Scraper, 'Words':Words}

@app.cli.command('createdb')
def createdb_command():
    '''
    Create our db & tables
    '''
    from sqlalchemy_utils import database_exists, create_database
    if not database_exists(SQLALCHEMY_DATABASE_URI):
        print('creating db')
        create_database(SQLALCHEMY_DATABASE_URI)
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
    # TODO: Test to see if we have the url already - if we do, we just return that id
    url_id = Scraper(url=myurl)
    db.session.add(url_id)
    db.session.commit()
    soup = souper(myurl)
    # Now we have stuff. let's do thing with it
    soup.get_url()
    soup.extract_stuff()
    soup.logic_up()
    common = soup.lemms_fdist.most_common(10)
    for sample in soup.lemms_fdist:
        v = soup.lemms_fdist[sample]
        w = Words(url = url_id.id, word = sample, wordcount = v)
        db.session.add(w)
    db.session.commit()

    return redirect(url_for('.get_by_id',url_id='{}'.format(url_id.id)))
    
@app.route('/url_id/<int:url_id>', methods=['GET'])
def get_by_id(url_id):
    '''
    Will return the words
    '''
    #w = db.session.query(Words).filter(Words.url==url_id)
    w = Words.query.filter(Words.url == url_id).all()
    return render_template('results.html', words = w)

if __name__ == '__main__':
    print('starting up...')
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    app.run()
