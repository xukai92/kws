'''
Python script to do keyword spotting.
Usage:
    python length.py query_file output_length_mapping
'''


import sys


# handle command line exception
if len(sys.argv) < 3:
    print '---\nUsage:\n    python length.py query_file output_length_mapping\n---\n'
    exit(1)

# read the query file into a dictionary
print 'reading xml file ...'
import xmltodict as xtd
with open(sys.argv[1]) as fd:   # query filename is the second argument
    queries = xtd.parse(fd.read())

# kws
print 'keyword spotting ...'
output = ''
count = {c: 0 for c in range(10)}
for query in queries['kwlist']['kw']:           # iterate over each query
    kwid = query['@kwid']
    word_list = (query['kwtext']).split(" ")    # get the word(s) in each query
    length = len(word_list)
    count[length] += 1
    output += str(length) + ' ' + kwid[6:] + ' ' + str(count[length]) + '\n'

# output
print "output file ..."
OUT_PATH = sys.argv[2]  # output filename is the third filename
f = open(OUT_PATH, "w")
f.write(output)
f.close()

print "... finished"
