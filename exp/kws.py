'''
Python script to do keyword spotting.
Usage:
    python kws.py index_file query_file output_decode_file
'''


import sys


# handle command line exception
if len(sys.argv) < 4:
    print '---\nUsage:\n    python kws.py index_file query_file output_decode_file\n---\n'
    exit(1)

# read index file into two dictionaries
# one for finding words
# one for detecting phrases
print 'reading index file ...'
f = open(sys.argv[1], "r")  # ctm filename is the head argument
lattices = {}
indices = {}
for line in f:
    line = line.replace('\n', '')
    line = line.split(' ')

    # indices
    if line[0] == 'LABEL':
        label = line[1]
        indices[label] = []
    elif line[0] == 'INFO':
        filen, ch, start, dur, pos, forw, backw = line[1:]
        start = float(start)
        dur = float(dur)
        pos = float(pos)
        indices[label].append({'filen': filen,
                               'ch': ch,
                               'start': start,
                               'dur': dur,
                               'pos': pos,
                               'forw': forw,
                               'backw': backw})

        # lattices
        if filen not in lattices.keys():
            lattices[filen] = []
        lattices[filen].append({'start': start,
                                'ch': ch,
                                'dur': dur,
                                'label': label,
                                'pos': pos})

f.close()

# read the query file into a dictionary
print 'reading xml file ...'
import xmltodict as xtd
with open(sys.argv[2]) as fd:   # query filename is the second argument
    queries = xtd.parse(fd.read())

# kws
print 'keyword spotting ...'
detected_kwlist = {}                            # to store detected kw
for query in queries['kwlist']['kw']:           # iterate over each query
    kwid = query['@kwid']
    word_list = (query['kwtext']).split(" ")    # get the word(s) in each query
    head = word_list[0]
    if head in indices.keys():
        query_length = len(word_list)
        if query_length == 1:     # single word
            for info in indices[head]:
                detected = {'kwfile': info['filen'],
                            'channel': '1',
                            'tbeg': info['start'],
                            'dur': info['dur'],
                            'score': info['pos'],
                            'decision': 'YES'}
                if kwid not in detected_kwlist.keys():
                    detected_kwlist[kwid] = []
                detected_kwlist[kwid].append(detected)
        else:                       # phrase
            for info in indices[head]:
                lattice = lattices[info['filen']]                       # the corresponding 1-best list
                lattice = sorted(lattice, key=lambda x: x['start'])     # sort with start time
                start_list = [entry['start'] for entry in lattice]      # ordered start time list
                label_list = [entry['label'] for entry in lattice]      # ordered label list
                head_index = start_list.index(info['start'])
                if head_index + query_length <= len(start_list):
                    if word_list == label_list[head_index:head_index + query_length]:
                        detected = {'kwfile': info['filen'],
                                    'channel': '1',
                                    'tbeg': info['start'],
                                    'dur': info['dur'],
                                    'score': info['pos'],
                                    'decision': 'YES'}
                        # check the 0.5s requirement
                        connected = True
                        for bias in range(query_length - 1):
                            if lattice[head_index + bias]['start'] + \
                                    lattice[head_index + bias]['dur'] + \
                                    0.5 >= lattice[head_index + bias + 1]['start']:
                                # if connected, update information
                                detected['score'] *= lattice[head_index + bias + 1]['pos']
                                detected['dur'] += lattice[head_index + bias + 1]['dur']
                            else:   # break if not meet 0.5s requirement
                                connected = False
                                break
                        if connected:   # output if connected
                            detected['dur'] = lattice[head_index + bias + 1]['start'] - \
                                              lattice[head_index]['start'] + \
                                              lattice[head_index + bias + 1]['dur']
                            if kwid not in detected_kwlist.keys():
                                detected_kwlist[kwid] = []
                            detected_kwlist[kwid].append(detected)

# format output
output = ""
output += '<kwslist kwlist_filename="IARPA-babel202b-v1.0d_conv-dev.kwlist.xml" language="swahili" system_id="">\n'
for kwid in detected_kwlist.keys():
    output += '<detected_kwlist kwid="{kwid}" oov_count="0" search_time="0.0">\n'.format(kwid=kwid)
    for kw in detected_kwlist[kwid]:
        output += '<kw file="{kwfile}" ' \
                  'channel="{channel}" ' \
                  'tbeg="{tbeg}" ' \
                  'dur="{dur}" ' \
                  'score="{score}" ' \
                  'decision="YES"/>\n'.format(kwfile=kw["kwfile"],
                                              channel=kw["channel"],
                                              tbeg=kw["tbeg"],
                                              dur=kw["dur"],
                                              score=kw["score"])
    output += '</detected_kwlist>\n'
output += "</kwslist>\n"

# output
print "output file ..."
OUT_PATH = sys.argv[3]  # output filename is the third filename
f = open(OUT_PATH, "w")
f.write(output)
f.close()

print "... finished"
