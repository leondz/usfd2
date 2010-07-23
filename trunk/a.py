import re
import tempEval2
from datetime import date
from timexIdentify import findTimexes,  buildSentenceList,  getTimexType,  getTimexValue


def findSubstrings(text, substring):
    # position pos (index) is moved up for each call to this generator
    pos = -1
    while True:
        # move index up on next call
        pos = text.find(substring, pos + 1)
        # not found or done
        if pos < 0:
            break
        yield pos
 


segmentationFile = '/home/leon/time/tempeval2/eval/entities/base-segmentation.tab'
dctFile = '/home/leon/time/tempeval2/eval/dct.txt'
extentsFile = 'timex-extents.tab'
attribsFile = 'timex-attributes.tab'


words = tempEval2.readSegmentation(segmentationFile)

timexes = findTimexes(words)


print "Results:"
for t in timexes:
#    print '(%s-%s) "%s"' % (doc_timex['start'],  doc_timex['end'],  doc_timex['text'])
    timexString = ' '.join(buildSentenceList(words[t['doc']][t['sentence']])[t['start']:t['end']+1])
    print t['doc'], t['sentence'], t['start'], t['end'],   timexString


extentsOut = open(extentsFile,  'w')
for t in timexes:
    for wordPosition in range(t['start'],  t['end'] + 1):
        extentsOut.write('\t'.join([t['doc'],  str(t['sentence']),  str(wordPosition),  'timex3',  't'+str(t['tid']), '1']) + '\n')
extentsOut.close

# read in DCTs for anchoring
dcts = {}

file = open(dctFile)
for line in file:
    docName,  docDct = line.strip().split('\t')
    dct = date(int(docDct[0:4]),  int(docDct[4:6]),  int(docDct[6:8]))
    dcts[docName] = dct


attrs = []

for t in timexes:
    sentenceList = buildSentenceList(words[t['doc']][t['sentence']])
    timexString = ' '.join(sentenceList[t['start']:t['end']+1])
    
    timexType = ''
    previous3Words = ' '.join(sentenceList[t['start']-3:t['start']-1])

    timexType = getTimexType(timexString,  previous3Words)
    
    docDate = dcts[t['doc']]
    timexValue = getTimexValue(timexString,  timexType,  docDate)

    # add one entry (for output file) per attribute
    if timexType:
        t['attr'] = 'type'
        t['value'] = timexType
        attrs.append(t.copy())
    
    if timexValue:
        
        
        t['attr'] = 'value'
        t['value'] = str(timexValue)
        attrs.append(t.copy())

    print timexString,  timexType,  timexValue
    

attribsOut= open(attribsFile,  'w')
for attr in attrs:
    attribsOut.write('\t'.join([attr['doc'],  str(attr['sentence']),  str(attr['start']),  'timex3',  't'+str(attr['tid']), '1',  attr['attr'],  attr['value']]) + '\n')
attribsOut.close()

