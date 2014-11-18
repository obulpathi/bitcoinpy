import sys
import getopt

_MAJOR=0
_MINOR=0
_REVISION=1

COPYRIGHT_YEAR=2014

VERSION = "%d.%d.%d" % (_MAJOR, _MINOR, _REVISION)

if __name__ == "__main__":
    for o,v in getopt.getopt(sys.argv[1:], 'vc')[0]:
        if o == '-v':
            print VERSION
        elif o == '-c':
            print COPYRIGHT_YEAR
