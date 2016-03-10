'''
Python script to do keyword spotting.
Usage:
    python kws.py ctm_file query_file output_decode_file
'''


import sys


# handle command line exception
if len(sys.argv) < 4:
    print "python kws.py ctm_file query_file output_decode_file"
    exit(1)

# read ctm file into a dictionary
# where the first level key is the filename
# and the second level key is the start time
print "reading ctm file ..."
f = open(sys.argv[1], "r")  # ctm filename is the first argument
lattices = {}
for line in f:
    temp_dict = {}
    line = " ".join(line.split())                   # remove the tabs
    line_list = line.replace("\n", "").split(" ")   # remove the line break symbol and convert to list
    file_name = line_list[0]
    temp_dict["channel"] = line_list[1]
    start_time = float(line_list[2])
    temp_dict["duration"] = float(line_list[3])
    temp_dict["token"] = line_list[4].lower()       # always input as lowercase
    temp_dict["word-posterior"] = float(line_list[5])
    if file_name not in lattices.keys():
        lattices[file_name] = {}
    lattices[file_name][start_time] = temp_dict
f.close()

# read the query file into a dictionary
print "reading xml file ..."
import xmltodict as xtd
with open(sys.argv[2]) as fd:   # query filename is the second argument
    queries = xtd.parse(fd.read())

# kws
print "keyword spotting ..."
detected_kwlist = {}                            # to store detected kw
for query in queries["kwlist"]["kw"]:           # iterate over each query
    word_list = (query['kwtext']).split(" ")    # get the word(s) in each query
    for file_name in lattices.keys():          # iterate over each file
        p_i = 0         # previous i
        # get the start time list in ascending order
        start_time_list = lattices[file_name].keys()
        start_time_list = sorted(start_time_list)
        while (p_i < len(start_time_list)):
            i = p_i + 1 # pointer for the file word list
            j = 0       # pointer for the query word list

            # find the first word
            found_start = False
            while (i < len(start_time_list)):
                entry = lattices[file_name][start_time_list[i]]
                if entry["token"] == word_list[j]:
                    found_start = True
                    break
                i += 1
            # i stores the index of the first word found now
            p_i = i     # backup it for next loop

            # check if the whole query is found
            if found_start:
                # compare the remaining part word-by-word
                while (j < len(word_list) and i < len(start_time_list)):
                    entry = lattices[file_name][start_time_list[i]]
                    if entry["token"] != word_list[j]:  # if not same
                        break                           # break
                    i += 1
                    j += 1
                found_query = False
                # if all the remaining part are the same
                # , j should be equal to the query length
                if j == len(word_list):
                    found_query = True

                # check 0.5s gap requirement
                if j > 1:   # only check when the query has multiple words
                    for k in range(j - 1):
                        if lattices[file_name][start_time_list[i - j + k]]["duration"] + \
                           start_time_list[i - j + k] < start_time_list[i - j + k + 1] - 0.5:
                            found_query = False
                            break

                if found_query:
                    # fetch record values
                    kwid = query["@kwid"]
                    start_time = start_time_list[i - j]
                    duration = lattices[file_name][start_time_list[i - 1]]["duration"] + \
                               start_time_list[i - 1] - start_time_list[i - j]
                    # compute score
                    nu = 0
                    for k in range(len(start_time_list)):
                        nu += lattices[file_name][start_time_list[k]]["word-posterior"]
                    denu = 0
                    for k in range(len(start_time_list)):
                        denu += lattices[file_name][start_time_list[k]]["word-posterior"]
                    posterior = nu / denu
                    score = posterior  # actually, for 1-best list, the score is always 1
                    # store it in a dictionary
                    detected = {"kwfile": file_name,
                                "channel": "1",
                                "tbeg": start_time,
                                "dur": duration,
                                "score": score,
                                "decision": "YES"}
                    # add it to the whole detected dictionary
                    if kwid not in detected_kwlist.keys():
                        detected_kwlist[kwid] = [detected]
                    else:
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
