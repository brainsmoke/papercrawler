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

class PaperSearch:

    PAPERS_DIR="papers/"
    QUERY_DIR="queries/"
    NEW_DIR="new/"
    QUERY_SYMLINK_BASE="../../"
    NEW_SYMLINK_BASE="../"

    TITLE_FILE="/title.txt"
    AUTHOR_FILE="/author.txt"
    CITATIONS_FILE="/citations.txt"
    BIBTEX_FILE="/bibtex.bib"
    ABSTRACT_FILE="/abstract.txt"
    PAPER_ORIGIN_FILE="/origin.txt"

    ## Data extraction part ############
    #
    #

    # Misc
    #

    def save_to_file(self, filename, string):
        f = file(filename, 'w')
        f.write(string)
        f.close()


    def normalize_whitespace(self, string):
        return re.sub('\s+', ' ', string).strip()


    # Search
    #

    def grab(self, regex, data):
        match = regex.search(data)
        if match == None:
            return None
        else:
            return match.group(1)

    def get_searchitem(self, itemdata):
        """
        Extracts a tuple (url, paper_descr, original_url) from the html-data
        of a single search item.
        """
        return (self.grab(self.page_url_regex, itemdata),
                self.grab(self.descr_regex, itemdata),
                self.grab(self.paper_url_regex, itemdata))


    def get_searchresults(self, page):
        """
        Extracts a list of tuples (url, paper_descr, original_url) from a
        single search page.
        """
        list_match = self.list_regex.search(page)

        if list_match == None:
            return []

        list = list_match.group()

        return map(lambda i: self.get_searchitem(i),\
                   self.items_regex.findall(list))


    def get_next_page_url(self, page):
        """
        Extracts the url for the next page
        """
        match = self.next_page_regex.search(page)

        if match == None:
            return None

        return self.SEARCH_BASE+match.group()

    # Single paper page
    #

    def is_busy(self, page):
        """
        Tests whether the returned page is a server-is-busy message
        """
        return self.busy_page_regex.search(page) != None


    def get_bibtex_entry(self, page):
        """
        Extracts the bibtex entry from a paper info page
        """
        match = self.bibtex_regex.search(page)

        if match == None:
            return None

        return match.group()


    def get_abstract(self, page):
        """
        Extracts the abstract from a paper info page
        """
        match = self.abstract_regex.search(page)

        if match == None:
            return None

        return match.group(1).strip()


    def get_citation_count(self, page):
        """
        Counts the number of citations on the page
        """
        citations_match = self.citations_regex.search(page)

        if citations_match == None:
            return 0

        return len(self.cite_count_regex.findall(citations_match.group()))


    def get_paper_urls(self, page):
        """
        Returns a list of urls to (cached) papers in several formats
        """
        papers_match = self.papers_regex.search(page)

        if papers_match == None:
            return []

        paper_items_matches = self.paper_item_regex.findall(papers_match.group())

        return paper_items_matches


    def get_paperdata(self, page):
        """
        Extracts (title, author, abstract, bibtex) from a paper info page
        """

        papers = self.get_paper_urls(page)

        abstract = self.get_abstract(page)

        bibtex = self.get_bibtex_entry(page)

        if bibtex == None:
            title_match = None
            author_match = None
        else:
            title_match = self.title_regex.search(bibtex)
            author_match = self.author_regex.search(bibtex)

        if title_match == None:
            title = None
        else:
            title = self.normalize_whitespace(title_match.group(1))

        if author_match == None:
            author = None
        else:
            author = self.normalize_whitespace(author_match.group(1))

        cite_count = self.get_citation_count(page)

        return (title, author, abstract, bibtex, cite_count, papers)


    ## Saving data #####################
    #
    #

    def check_directories(self):
        """
        Creates directories if necessary
        """

        if not exists(self.PAPERS_DIR):
            makedirs(self.PAPERS_DIR)

        if not exists(self.QUERY_DIR):
            makedirs(self.QUERY_DIR)

        if not exists(self.NEW_DIR):
            makedirs(self.NEW_DIR)


    def create_query_dir(self, query):
        """
        Creates and returns a new directory 
        """

        iter=0
        while exists(self.QUERY_DIR+query+"_"+str(iter)):
            iter+=1
        else:
            query_dir=self.QUERY_DIR+query+"_"+str(iter)+"/"

        makedirs(query_dir)
        print "Created directory "+query_dir

        return query_dir


    def save_data(self, paper_dir, title, author, cite_count, bibtex, abstract, origin):
        self.save_to_file(paper_dir+self.TITLE_FILE, str(title)+"\n")
        self.save_to_file(paper_dir+self.AUTHOR_FILE, str(author)+"\n")
        self.save_to_file(paper_dir+self.CITATIONS_FILE, str(cite_count)+"\n")
        self.save_to_file(paper_dir+self.BIBTEX_FILE, str(bibtex)+"\n")
        self.save_to_file(paper_dir+self.ABSTRACT_FILE, str(abstract)+"\n")
        self.save_to_file(paper_dir+self.PAPER_ORIGIN_FILE, str(origin)+"\n")


    def do_search(self, query, query_dir):

        print "Searching for \""+query+"\""

        self.check_directories()

        iter = 0

        search_url = self.get_search_url(query)

        papers = []

        while search_url != None:

            filename = query_dir+"search_"+str(iter)+".html"
            iter+=1

            print "Retrieving \""+search_url+"\""
            urllib.urlretrieve(search_url, filename)
            f = file(filename)
            page = f.read()
            f.close()

            papers += self.get_searchresults(page)

            search_url = self.get_next_page_url(page)

        return papers


    def download_page(self, url, filename):

        try:
            urllib.urlretrieve(url, filename)
            f = file(filename)
            page = f.read()
            f.close()

            wait_secs = 5
            while self.is_busy(page):
                sys.stderr.write("Busy, timeout(%d)..." % (wait_secs))
                time.sleep(wait_secs)
                wait_secs *= 2
                sys.stderr.write("retrying\n")

                urllib.urlretrieve(url, filename)
                f = file(filename)
                page = f.read()
                f.close()

            return page
        except IOError:
            remove(filename)
            return None


    def sort_papers(self, papers):
        extensions = [ ".pdf", ".ps.gz", ".ps" ]
        extensions.reverse()
        p = papers

        for ext in extensions:
            for i in range(len(papers)):
                tmp = p[i]
                if tmp.lower().endswith(ext):
                    p[i:i+1] = []
                    p[0:0] = [tmp]
        return p
    

    def download_paper(self, paper_dir, papers):

        for paper in papers:
            try:
                filename = None
                f_in = urllib.urlopen(paper)
                paperdata = f_in.read()
                filename = paper_dir+"/"+self.get_paper_filename(f_in.geturl())
                f_out = file(filename, 'wb')
                f_out.write(paperdata)
                f_out.close()
                
                break
            except IOError:
                if filename and exists(filename):
                    remove(filename)
        else:
            sys.stderr.write("WARNING: could not download "\
                "any alternative for: "+ str(filename)+"\n")


    def retrieve_papers(self, query, limit=None):

        query_dir = self.create_query_dir(query)

        papers = self.do_search(query, query_dir)

        download_count = 0

        for (page_url, title, paper_url) in papers:
            paper_id = self.get_paper_id(page_url)
            paper_dir = self.PAPERS_DIR+paper_id

            if exists(paper_dir):
                continue

            if paper_url == None:
                print "WARNING: skipping "+title
                continue

            print paper_id+": "+title

            makedirs(paper_dir)

            page_filename = paper_dir+"/"+basename(page_url)
            page = self.download_page(self.SEARCH_BASE+page_url, page_filename)

            if page == None:
                rmdir(paper_dir)
                continue

            (title, author, abstract, bibtex, cite_count, cache) = \
                self.get_paperdata(page)

            self.download_paper(paper_dir,\
                [self.PAPER_BASE+paper_url]+self.sort_papers(cache))

            symlink(self.QUERY_SYMLINK_BASE+paper_dir, query_dir+paper_id)
            symlink(self.NEW_SYMLINK_BASE+paper_dir, self.NEW_DIR+paper_id)

            self.save_data(paper_dir, title, author, cite_count,\
                           bibtex, abstract, self.SEARCH_BASE+page_url)

            download_count += 1
            if limit != None and download_count >= limit:
                break

