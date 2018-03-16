# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, render_template, request, redirect, url_for)
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import os
from .scraper import souper

app = Flask(__name__)

def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected variable {} unset".format(name)
        return message

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
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']

# A list of words to use for storing n stuff
our_words = ['the', 'this','many', 'python', 'mysql'] 
db = SQLAlchemy(app)


# Migrations
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


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

    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id' : self.id,
           'url': self.url, 
       }


class Words(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    word = db.Column(db.String(50), unique = False, nullable = False)
    wordcount = db.Column(db.Integer)
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id' : self.id,
           'url': self.url, 
           'word' : self.word,
           'wordcount' : self.wordcount,
       }
################################################################################


@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Scraper':Scraper, 'Words':Words}

#@app.cli.command('createdb')
#def createdb_command():
#    '''
#    Create our db & tables
#    '''
#    from sqlalchemy_utils import database_exists, create_database
#    if not database_exists(SQLALCHEMY_DATABASE_URI):
#        print('creating db')
#        create_database(SQLALCHEMY_DATABASE_URI)
#    print('creating tables')
#    db.create_all()
#    print('done')

@app.route('/')
def index():
    '''
    Will take a url and parse the fucker
    TODO: get url from get args
    '''
    import json
    last_n = Scraper.query.filter().order_by(Scraper.id).limit(20)
    data = json.dumps([i.serialize() for i in last_n])
    return render_template('index.html', data = data, last_n = last_n)

@app.route('/add', methods=['POST'])
def add_url():
    myurl = request.form['url']
    if len(myurl) == 0:
        return redirect('/')

    have_url = Scraper.query.filter(Scraper.url == myurl).all()
    if len(have_url) > 0:
        print('we have some of those')
        return redirect('/')

    # This is our nltk stuff
    soup = souper(myurl)
    res = soup.get_url()
    if res == False:
        return  redirect('/')

    url_id = Scraper(url=myurl)
    db.session.add(url_id)
    db.session.commit()

    soup.extract_stuff()
    soup.logic_up()
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
    import json
    w = Words.query.filter(Words.url == url_id).all()
    data = json.dumps([i.serialize for i in w])
    return render_template('results.html', words = w, data = data, url_id = url_id)

@app.route('/url_wc/<int:url_id>', methods=['GET'])
def get_faves(url_id):
    import json
    w = Words.query.filter(Words.url == url_id).all() #.having(Words.word in our_words).all()
    data = json.dumps([i.serialize for i in w if i.word in our_words])
    print(data)
    return render_template('results.html', words = w, data = data, url_id = None)
    

if __name__ == '__main__':
    print('starting up...')
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    app.run()
