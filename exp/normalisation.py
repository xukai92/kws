'''
Python script to do score normalisation
Usage:
    python normalisation.py kws_file gamma normalised_kws_file
'''


import sys


# handle command line excetion
if len(sys.argv) < 4:
    print "---\nUsage:\n    python normalisation.py kws_file gamma normalised_kws_file\n---\n"
    exit(1)

# read kws file into a dictionary
print "reading kws file ..."
import xmltodict as xtd
with open(sys.argv[1]) as fd:
    decode = xtd.parse(fd.read())

# score normalisation
print "normalising scores ..."
gamma = float(sys.argv[2])
for detected_kwlist in decode['kwslist']['detected_kwlist']:
    sum = 0
    if 'kw' in detected_kwlist.keys():
        if type(detected_kwlist['kw']) == type([]):     # if multiple hits
            for kw in detected_kwlist['kw']:
                sum += float(kw['@score']) ** gamma
            for kw in detected_kwlist['kw']:
                kw['@score'] = float(kw['@score']) ** gamma / sum
        else:
            kw = detected_kwlist['kw']
            kw['@score'] = 1.


# output
output = ""
output += '<kwslist kwlist_filename="IARPA-babel202b-v1.0d_conv-dev.kwlist.xml" language="swahili" system_id="">\n'
for detected_kwlist in decode['kwslist']['detected_kwlist']:
    kwid = detected_kwlist['@kwid']
    output += '<detected_kwlist kwid="{kwid}" oov_count="0" search_time="0.0">\n'.format(kwid=kwid)
    if 'kw' in detected_kwlist.keys():
        if type(detected_kwlist['kw']) == type([]):     # if there are multiple hits
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
OUT_PATH = sys.argv[3]
f = open(OUT_PATH, "w")
f.write(output)
f.close()

print "... finished"
