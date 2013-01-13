#!/usr/bin/env python
# moves a symlink, keeping it pointing at the same file
# keeps relative links relative, and absolute links absolute
# no further guarantees :-)

from os import *
from os.path import *
from sys import *

if len(argv) != 3 or not islink(argv[1]) or argv[2] == "":
    print "Usage: %s <symlink> <dest>" % ( argv[0] )
    exit(1)

src, dest = argv[1:]

if isdir(dest) or dest[-1] == '/':
    dest += "/"+basename(src)

if isfile(dest):
    print "Destination already exists (and is not a directory)"
    exit(1)

src, dest = abspath(src), abspath(dest)
src_dir, dest_dir = dirname(src), dirname(dest)

if not exists(dest_dir):
    print "Destination directory does not exist"
    exit(1)

src_sym = readlink(src)
if src_sym[0] != '/':
    sym_path = abspath(join(src_dir, src_sym)).split('/')
    dest_path = dest_dir.split('/')

    while len(sym_path) > 0 and len(dest_path) > 0:
        if sym_path[0] == dest_path[0]:
            sym_path[0:1] = []
            dest_path[0:1] = []
        else:
            break

    dest_sym = '/'.join(['..']*len(dest_path)+sym_path)
else:
    dest_sym = src_sym

symlink(dest_sym, dest)
remove(src)
