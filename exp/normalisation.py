'''
Usage:
    python normalisation.py decode_file output_normalised_decode_file
'''

import sys

import xmltodict as xtd
with open(sys.argv[1]) as fd:
    decode = xtd.parse(fd.read())

for detected_kwlist in decode['kwslist']['detected_kwlist']:
    sum = 0
    if 'kw' in detected_kwlist.keys():
        if type(detected_kwlist['kw']) == type([]):
            for kw in detected_kwlist['kw']:
                sum += float(kw['@score'])
            for kw in detected_kwlist['kw']:
                kw['@score'] = float(kw['@score']) / sum


# output
output = ""
output += '<kwslist kwlist_filename="IARPA-babel202b-v1.0d_conv-dev.kwlist.xml" language="swahili" system_id="">\n'
for detected_kwlist in decode['kwslist']['detected_kwlist']:
    kwid = detected_kwlist['@kwid']
    output += '<detected_kwlist kwid="{kwid}" oov_count="0" search_time="0.0">\n'.format(kwid=kwid)
    if 'kw' in detected_kwlist.keys():
        if type(detected_kwlist['kw']) == type([]):
            for kw in detected_kwlist['kw']:
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
        else:
            kw = detected_kwlist['kw']
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
OUT_PATH = sys.argv[2]
f = open(OUT_PATH, "w")
f.write(output)
f.close()

print "... finished"
