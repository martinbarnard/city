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
        return ' '.join(compile(r'\W+', UNICODE).split(txt))

    def get_url(self):
        '''
        Will parse the given url and return the tokenised text
        '''
        # try to get our site - note some 403's depending upon sophistication of the site
        # todo: test & return / raise error
        site = urllib.request.urlopen(self.url)
        self.html = site.read()
        site.close()
        return True

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
        wnl = nltk.WordNetLemmatizer()
        txt = self.cleaned_text

        # tokenisze
        self.tokens = nltk.word_tokenize(txt)

        # After tokenization
        # lemmatize
        self.lemms = [wnl.lemmatize(t) for t in self.tokens]

        # frequency distribution
        #self.token_fdist = nltk.FreqDist(w for w in self.tokens)
        self.lemms_fdist = nltk.FreqDist(w for w in self.lemms)
        return True


if __name__=='__main__':
    # Really, just an example
    print('''calling souper with 'http://www.wikipedia.org'...''')
    soup = souper('https://www.wikipedia.org')
    print('soup.get_url() example')
    soup.get_url()
    print('soup.extract_stuff() example')
    soup.extract_stuff()
    print('soup.logic_up() example')
    soup.logic_up()
    print('Most Common 10 words:')
    print(soup.lemms_fdist.most_common(10))

