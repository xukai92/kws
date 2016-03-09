'''
Usage:
    python decompose.py
'''

# read query morph dict
print 'reading query morph dict ...'
f = open('lib/dicts/morph.kwslist.dct', 'r')
query_dict = {}
for line in f:
    d = line.strip().split("\t")
    query_dict[d[0]] = d[1]
f.close()

# read queries
print 'reading queries ...'
import xmltodict as xtd
with open('lib/kws/queries.xml') as f:
    queries = xtd.parse(f.read())
queries_morph = {}
for query in queries['kwlist']['kw']:
    words = query['kwtext'].split(" ")
    for i in range(len(words)):
        if words[i] in query_dict.keys():
            words[i] = query_dict[words[i]]
    queries_morph[query['@kwid']] = ' '.join(words)

# decompose queries
print 'decomposing queries'
f = open('exp/queries-morph.xml', 'w')
f.write('<kwlist ecf_filename="IARPA-babel202b-v1.0d_conv-dev.ecf.xml" language="swahili" encoding="UTF-8" compareNormalize="lowercase" version="202 IBM and BBN keywords">\n')
for kwid in queries_morph:
    out = '  <kw kwid="{kwid}">\n'.format(kwid=kwid)
    out += "    <kwtext>{kwtext}</kwtext>\n".format(kwtext=queries_morph[kwid])
    out += '  </kw>\n'
    f.write(out)
f.write('</kwlist>')
f.close()

# read 1-best morph dict
print 'reading ctm morph dict ...'
f = open('lib/dicts/morph.dct', 'r')
onebest_dict= {}
for line in f:
    d = line.strip().split('\t')
    onebest_dict[d[0]] = d[1]
f.close()

# read 1-best
print 'reading ctm file ...'
ctm = []
f = open('lib/ctms/decode.ctm', 'r')
for line in f:
    entry = line.split()
    token = entry[4]
    if token in onebest_dict.keys():
        token = onebest_dict[token]
    token = token.split()
    entry[4] = token
    ctm.append(entry)
f.close()

# decompose 1-best
print 'decomposing ctm file ...'
f = open('exp/decode-morph.ctm', 'w')
for entry in ctm:
    l = len(entry[4])
    dur = float(entry[3]) / l
    post = float(entry[5]) ** (1.0 / l)
    for i in range(l):
        start = float(entry[2]) + dur * (i - 1)
        out = '{f} 1 {start} {dur} {token} {post}\n' \
              .format(f=entry[0],
                      start=start,
                      dur="{0:.2f}".format(dur),
                      token=entry[4][i],
                      post=post)
        f.write(out)
f.close()

print '... finished'
