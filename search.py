#!/usr/bin/env python
import sys
import acm, citeseer

usage = """
Usage: %s [--limit <number>] acm|citeseer <query>

    --limit <number>   Limits the number of newly downloaded papers

    if <query> consists of more than one argument, these will be
    concatenated with spaces in between.


Downloads papers from online libraries.

The following directory structure is created:

papers/
    <unique paper ids>/   (format: <site id> "." <paper id>)
        title.txt
        author.txt
        citations.txt     (no. of references to this paper, citeseer only)
        bibtex.bib
        abstract.txt
        origin.txt

new/
    <symlinks to papers>

queries/
    <query names>/
        search_<number>.html   (saved search query results)
        <symlinks to papers>

For ACM, a proxy may be necessary in order to get access to the library.
The 'http_proxy' environment variable is used automatically by python if set.

Examples:

python search.py citeseer smart phones
http_proxy='http://www-proxy.few.vu.nl:8080' python search.py acm smart phones

"""

def exit_error():
    sys.stderr.write(usage % sys.argv[0])
    sys.exit(1)

limit = None

while len(sys.argv) > 1:
    if sys.argv[1] == "--help":
        exit_error()

    if sys.argv[1] == "--limit":
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            limit = int(sys.argv[2])
            sys.argv[1:3] = []
        else:
            exit_error()

    if sys.argv[1].lower() == "acm":
        search = acm.AcmSearch()
        sys.argv[1:2] = []
        break

    if sys.argv[1].lower() == "citeseer":
        search = citeseer.CiteseerSearch()
        sys.argv[1:2] = []
        break
else:
    exit_error()

query = " ".join(sys.argv[1:])

search.retrieve_papers(query, limit)

