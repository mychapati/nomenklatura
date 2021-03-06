
OP_EQ = '=='
OP_IN = '|='
OP_NOT = '!='
OP_NIN = '|!='
OP_LIKE = '~='
OP_SIM = '%='


def parse_name(name):
    inverted, op = False, OP_EQ
    if name is not None:
        for op_ in (OP_NIN, OP_IN, OP_NOT, OP_LIKE, OP_SIM):
            if name.endswith(op_):
                op = op_
                name = name[:len(name) - len(op)]
                break
        if name.startswith('!'):
            inverted = True
            name = name[1:]
    return name, inverted, op
