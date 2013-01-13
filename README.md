A (most-probably outdated) paper crawler for ACM/Computer.org/Citeseer
which I coded back in 2007 to aid me in finding papers.

Usage: python search.py [--limit <number>] acm|citeseer <query>

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
http_proxy='http://<your-uni's proxy>:8080' python search.py acm smart phones

