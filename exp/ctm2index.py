'''
Python script to convert ctm file to index file.
Usage:
    python ctm2index.py ctm_file index_file
'''


import sys


# handle command line exception
if len(sys.argv) < 3:
    print '---\nUsage:\n    python ctm2index.py ctm_file index_file\n---\n'
    exit(1)

# read ctm file into an index dictionary
print 'reading ctm file ...'
f = open(sys.argv[1], "r")  # ctm filename is the first argument
indices = {}
for line in f:
    info_dict = {}
    line = " ".join(line.split())                   # remove the tabs
    line = line.replace("\n", "")                   # remove the line break symbol
    line_list = line.split(" ")                     # convert it to list

    info_dict['filen'] = line_list[0]
    info_dict["ch"] = line_list[1]
    info_dict["start"] = float(line_list[2])
    info_dict["dur"] = float(line_list[3])
    label = line_list[4].lower()                    # always input as lowercase
    info_dict["pos"] = float(line_list[5])
    info_dict["forw"] = 1
    info_dict["backw"] = 1

    if label not in indices.keys():
        indices[label] = []
    indices[label].append(info_dict)
f.close()

# write the index dictionary to an index file
output = ''
for label in indices.keys():
    output += 'LABEL {label}\n'.format(label=label)
    for info in indices[label]:
        output += 'INFO {filen} {ch} {start} {dur} {pos} {forw} {backw}\n' \
                  .format(filen=info['filen'],
                          ch=info['ch'],
                          start=info['start'],
                          dur=info['dur'],
                          pos=info['pos'],
                          forw=info['forw'],
                          backw=info['backw'])

# output
print 'outputting index file ...'
OUT_PATH = sys.argv[2]  # output filename is the third filename
f = open(OUT_PATH, "w")
f.write(output)
f.close()

print "... finished"
