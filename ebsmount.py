#!/usr/bin/python
"""Example command template

Options:
  -q --quiet	don't print anything
  -f=FOO	print FOO
  --fatal       fatal error

"""
import sys
import getopt

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Syntax: %s [args]" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()
    sys.exit(1)

def fatal(s):
    print >> sys.stderr, "error: " + str(s)
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'qf:h', ['fatal'])
    except getopt.GetoptError, e:
        usage(e)

    opt_quiet = False
    for opt, val in opts:
        if opt == '-h':
            usage()

        if opt in ('-q', '--quiet'):
            opt_quiet = True

        elif opt == '-f':
            print "printing foo: " + val

        elif opt == '--fatal':
            fatal("fatal condition")

    if not opt_quiet:
        print "printing args: " + `args`

    
if __name__=="__main__":
    main()

