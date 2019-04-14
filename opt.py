from functools import partial
from optparse import OptionParser
from os import path

from base import Left, Right, Either, compose

usage = "show something usefull -- for example: how to use this program"
parser = OptionParser(usage)
parser.add_option("-f", "--file", dest="filename", help="read picture from File", metavar="FILE", action="store",
                  type="string")
parser.add_option("-o", "--output", dest="output", help="out picture from File", action="store",
                  default=Left(Exception("Must set!")), type="string")

fakeArgs = ['-o', 'file.txt;file_2.txt', 'how are you', 'arg1', 'arg2']


class IsAFileError(IsADirectoryError):
    pass


def option(exception):
    def wrapper(predicate):
        def ret(*args, **kwargs):
            if predicate(*args, **kwargs):
                return Right(*args, **kwargs)
            else:
                return Left(exception(*args, **kwargs))

        return ret

    return wrapper


exists = option(FileNotFoundError)(path.exists)
isfile = option(IsAFileError)(path.isfile)
isdir = option(IsADirectoryError)(path.isdir)

op, ar = parser.parse_args(fakeArgs)
for key, value in op.__dict__.items():
    if isinstance(value, Either):
        continue
    else:
        setattr(op, key, Right(value))
# filter = compose(list, filter)
out = op.output
files = compose(list, partial(filter, lambda s: s != ''), partial(str.split, sep=';'))

files = out.map(files)

files.map()
