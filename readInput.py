import re

def segSent(line, qre, are):
    q = qre.match(line)
    if q:
        return q.groups()
    else:
        return are.match(line).groups()

def getSentences (file):
    qre = re.compile('^(\d+) (.*) \\t(.*)\\t(.*)\\n')
    are = re.compile('(^\d+) (.*)\\n')
    f = open(file, 'r')
    sents = []
    line = f.readline()
    while line:
        sent = segSent(line, qre, are)
        # print sent
        sents.append(sent)
        line = f.readline()
    return sents
