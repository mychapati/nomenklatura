#
# Python parser/writer for factish files
#

import shlex
import json
import re

PLAIN = re.compile(r"^[a-zA-Z_\$\@][a-zA-Z0-9_\$\@]*$", re.M | re.I)
EXP_END = ';'
EXP_SOURCE = '$'
EXP_ATTRIB = '@'


def decode_value(token):
    if PLAIN.match(token):
        return token
    return json.loads(token)


def expressions(fh):
    lexer = shlex.shlex(fh)
    base_exp = {'t': 'statement'}
    exp = base_exp.copy()
    while True:
        if exp is None:
            exp = base_exp.copy()
        token = lexer.get_token()
        if token is lexer.eof:
            break
        if token == EXP_END:
            yield exp
            exp = base_exp.copy()
            continue
        print token
        value = decode_value(token)
        print [token, value]


with open('sample.fish', 'r') as fh:
    for exp in expressions(fh):
        print exp
