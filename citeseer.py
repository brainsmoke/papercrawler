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

class CiteseerSearch(PaperSearch):

    SEARCH_BASE=""
    PAPER_BASE="http://"

    def get_paper_id(self, url):
        return "citeseer."+basename(url)[:-5]

    def get_search_url(self, query):
        return "http://citeseer.ist.psu.edu/cis?"+\
               urllib.urlencode({'q': query, 'cs':1})

    def get_paper_filename(self, url):
        return basename(url)

    #
    # Regular expressions
    #

    page_url_regex = re.compile(\
        '<a href="(.*?)">.*?</a>.*?<font color=green>.*?</font>',
        re.M|re.S)

    descr_regex = re.compile(\
        '<a href=".*?">(.*?)</a>.*?<font color=green>.*?</font>',
        re.M|re.S)

    paper_url_regex = re.compile(\
        '<a href=".*?">.*?</a>.*?<font color=green>(.*?)</font>',
        re.M|re.S)

    list_regex = re.compile(\
        '(?<=<!--RLS-->).*?(?=<!--RLE-->)', re.M|re.S)

    items_regex = re.compile(\
        '(?<=<!--RIS-->).*?(?=<!--RIE-->)', re.M|re.S)

    bibtex_regex = re.compile(\
        '(?<=<!--gbr--><br><!--gbr2--><pre>).*?(?=</pre>)', re.M|re.S)

    abstract_regex = re.compile(\
        '<=^<b>Abstract:</b>(.*?)<a href="', re.M|re.S)

    author_regex = re.compile(\
        '^\s*author\s*=\s*"(.*?)"', re.M|re.S)

    title_regex = re.compile(\
        '^\s*title\s*=\s*"(.*?)"', re.M|re.S)

    next_page_regex = re.compile(\
        '(?<=<a href=")http://citeseer\.ist\.psu\.edu/cs\?qb=[^"]*?'\
        '(?=">Next 20</a><br>)')

    citations_regex = re.compile(\
        '(?<=<b> Citations \(may not include all citations\):</b>).*?'\
        '(?=<b> Documents on the same site |<!-- ddv:)', re.M|re.S)

    cite_count_regex = re.compile(\
        '<a class=', re.M|re.S)

    papers_regex = re.compile(\
        '^Cached:&nbsp;&nbsp;.*$', re.M)

    paper_item_regex = re.compile(\
        '(?<=<a href=").*?(?=")')

    busy_page_regex = re.compile(\
        '^<span class=m><center><font size=\+2><b>'\
        'System busy\. Try again later\.', re.M)


if __name__ == '__main__':
    search = CiteseerSearch()
    query = ' '.join(sys.argv[1:])
    search.retrieve_papers(query)

