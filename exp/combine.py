'''
Usage:
    python combine.py decode_file_1 decode_file_2 output_combined_decode_file
'''

import sys
if len(sys.argv) < 4:
    print "python combine.py decode_file_1 decode_file_2 output_combined_decode_file"
    exit(1)

import xmltodict as xtd
with open(sys.argv[1]) as fd:
    decode_1 = xtd.parse(fd.read())

with open(sys.argv[2]) as fd:
    decode_2 = xtd.parse(fd.read())

decode = {}

print 'reading file 1 ...'
for detected_kwlist in decode_1['kwslist']['detected_kwlist']:
    kwid = detected_kwlist['@kwid']
    decode[kwid] = []
    if 'kw' in detected_kwlist.keys():
        if type(detected_kwlist['kw']) == type([]):
            for kw in detected_kwlist['kw']:
                decode[kwid].append(kw)
        else:
            kw = detected_kwlist['kw']
            decode[kwid].append(kw)

print 'reading file 2 ...'
for detected_kwlist in decode_2['kwslist']['detected_kwlist']:
    kwid = detected_kwlist['@kwid']
    if kwid not in decode.keys():
        decode[kwid] = []
    if 'kw' in detected_kwlist.keys():
        if type(detected_kwlist['kw']) == type([]):
            for kw in detected_kwlist['kw']:
                decode[kwid].append(kw)
        else:
            kw = detected_kwlist['kw']
            decode[kwid].append(kw)


# output
output = ""
output += '<kwslist kwlist_filename="IARPA-babel202b-v1.0d_conv-dev.kwlist.xml" language="swahili" system_id="">\n'
for kwid in decode.keys():
    output += '<detected_kwlist kwid="{kwid}" oov_count="0" search_time="0.0">\n'.format(kwid=kwid)
    for kw in decode[kwid]:
        output += '<kw file="{kwfile}" ' \
                  'channel="{channel}" ' \
                  'tbeg="{tbeg}" ' \
                  'dur="{dur}" ' \
                  'score="{score}" ' \
                  'decision="YES"/>\n'.format(kwfile=kw["@file"],
                                              channel=kw["@channel"],
                                              tbeg=kw["@tbeg"],
                                              dur=kw["@dur"],
                                              score=kw["@score"])
    output += '</detected_kwlist>\n'

output += "</kwslist>\n"

print "output file ..."
OUT_PATH = sys.argv[3]
f = open(OUT_PATH, "w")
f.write(output)
f.close()

print "... finished"
