#!/usr/bin/env python3
# scraper module
import nltk
import urllib
from bs4 import BeautifulSoup as bs

# Probably have some default thing for this
#stopwords = nltk.corpus.stopwords('english')

class souper():
    '''
    All of these things will only work if they are pipelined first
    '''
    def __init__(self, url):
        self.url = url
        self.url_parsed = False
        self.html_parsed = False
        self.html = ''
        self.text_extracted = False
        self.extracted_text = ''
        self.tokens = []
        self.fdist = {}
        self.lemms = []
        
    def _strip_nonalpha(self, txt):
        '''
        Internal function to strip non alphanumeric
        param: txt
        return: txt
        '''
        from re import compile, UNICODE
        
        rv = ' '.join(compile(r'\W+', UNICODE).split(txt))
        return rv

    def get_url(self):
        '''
        Will parse the given url and return the tokenised text
        '''
        # try to get our site - note some 403's depending upon sophistication of the site
        # todo: test & return / raise error
        try:
            site = urllib.request.urlopen(self.url)
            self.html = site.read()
            site.close()
            return True
        except:
            print('unable to open site')
            print(self.url)
            return False

    def extract_stuff(self):
        soup = bs(self.html, 'html.parser')
        # get rid of crap
        for script in soup(['script', 'style']):
            script.extract()

        # Now, we have a few ways of getting clean text
        self.extracted_text = soup.get_text(' ', True).lower()
        self.cleaned_text = self._strip_nonalpha(self.extracted_text)
        return True

    def logic_up(self):
        '''
        Do our simple logic and stuff
        '''
        from nltk.corpus import stopwords
        wnl = nltk.WordNetLemmatizer()
        txt = self.cleaned_text

        # tokenisze
        self.tokens = nltk.word_tokenize(txt)

        # After tokenization
        # lemmatize
        self.lemms = [wnl.lemmatize(t) for t in self.tokens]
        # Remove our stopwords
        self.stripped = [w for w in self.lemms if w not in stopwords.words('english')]
        self.stripped_fdist = nltk.FreqDist(w for w in self.stripped if len(w)>3)

        # frequency distribution
        #self.token_fdist = nltk.FreqDist(w for w in self.tokens)
        self.lemms_fdist = nltk.FreqDist(w for w in self.lemms)
        return True


