#
# Copyright (c) 2007 Erik Bosman <ejbosman@cs.vu.nl>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a  copy  of  this  software  and  associated  documentation  files
# (the "Software"),  to  deal  in  the  Software  without  restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit  persons to whom  the Software is  furnished to do so,
# subject to the following conditions:
#
# The  above  copyright notice and  this permission notice  shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#

import re
import sys
import time
from os import *
from os.path import *
import urllib

from papersearch import PaperSearch

class AcmSearch(PaperSearch):

    SEARCH_BASE="http://portal.acm.org/"
    PAPER_BASE="http://portal.acm.org/"

    def get_paper_id(self, url):
        tmp = basename(url).split('id=', 1)[1]
        id = basename(tmp).split('&', 1)[0]
        return "acm."+id

    def get_search_url(self, query):
        return "http://portal.acm.org/results.cfm/?"+\
            urllib.urlencode({'query': query, 'querydisp':query, 'start':1,
                              'slide':1, 'srt':'score dsc', 'short':0,
                              'parser':'Internet', 'source_parser':'Internet',
                              'source_disp':'', 'source_query':'',
                              'coll':'Portal', 'dl':'GUIDE'})

    def get_paper_filename(self, url):
        tmp = url.split('?',1)[0]
        return basename(tmp)

    #
    # Override
    #

    bibtex_2_regex = re.compile('<PRE id=".*">([^<]*)</pre>', re.M|re.S)

    def get_bibtex_entry(self, page):
        try:
            url = PaperSearch.get_bibtex_entry(self, page)
            f = urllib.urlopen(self.SEARCH_BASE+url)
            bibtex = f.read()
            match = self.bibtex_2_regex.search(bibtex)
            if match:
                bibtex = match.group(1)
            else:
                bibtex = None
            f.close()
        except IOError:
            bibtex = None

        return bibtex

    #
    # Regular expressions
    #

    page_url_regex = re.compile(\
        '<td colspan="3">\s*<A HREF="(.*?)".*?>.*?</A>', re.M|re.S)

    descr_regex = re.compile(\
        '<td colspan="3">\s*<A HREF=".*?".*?>(.*?)</A>', re.M|re.S)

    paper_url_regex = re.compile(\
        '(?<=<A HREF=")(ft_gateway.cfm.*?)"', re.M|re.S)

    list_regex = re.compile(\
        '(?<=<table border="0">).*?'\
        '^<table border="0" width="100%" align="left" class="small-text">',\
        re.M|re.S)

    items_regex = re.compile(\
        '(?<=<td class="small-text" align="center" valign="top"> <strong>)'\
        '(.*?(?=<td class="small-text" align="center" valign="top"> <strong>)|'\
        '.*?^<table border="0" width="100%" align="left" class="small-text">)',\
        re.M|re.S)

    bibtex_regex = re.compile("popBibTex.cfm[^']*(?=')", re.M|re.S)

    abstract_regex = re.compile(\
        '>ABSTRACT</A></span>\s*<p class="abstract">\s*<p>(.*?)</p>',
        re.M|re.S)

    author_regex = re.compile(\
        '^\s*author\s*=\s*["{](.*?)["}]', re.M|re.S)

    title_regex = re.compile(\
        '^\s*title\s*=\s*["{](.*?)["}]', re.M|re.S)

    next_page_regex = re.compile(\
        '(?<=<a href=")results.cfm\?query=[^"]*?(?=">\s*next</a>)', re.M|re.S)

    # ACM does not do reverse reverences (or I havent found them)
    citations_regex = re.compile('^ABCDE$')
    cite_count_regex = re.compile('^EDCBA$')

    # no alternative download locations either
    papers_regex = re.compile("^$")
    paper_item_regex = re.compile("^$")

    # no known busy page for ACM
    busy_page_regex = re.compile("^$")


if __name__ == '__main__':
    search = AcmSearch()
    query = ' '.join(sys.argv[1:])
    search.retrieve_papers(query)

