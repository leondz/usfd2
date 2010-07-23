import re
from datetime import date,  timedelta
import tempEval2
from timexIdentify import findTimexes,  buildSentenceList,  getTimexType


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
 


segmentationFile = '/home/leon/time/tempeval2/test/english/entities/base-segmentation.tab'
dctFile = '/home/leon/time/tempeval2/test/english/dct.txt'
extentsFile = 'timex-extents.tab'
attribsFile = 'timex-attributes.tab'

futureLimit = 14


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
numbersRx = re.compile(r'^[0-9]+ ')

for t in timexes:
    sentenceList = buildSentenceList(words[t['doc']][t['sentence']])
    timexString = ' '.join(sentenceList[t['start']:t['end']+1])
    
    timexType = ''
    previous3Words = ' '.join(sentenceList[t['start']-3:t['start']-1])

    timexType = getTimexType(timexString,  previous3Words)
    
    timexValue = None
    if timexString.lower == 'today' or timexString.lower == 'now':
        timexValue = 'PRESENT_REF'
    
    timexValueComplete = False
    timexValue = 'P'
    
    distance = ''
    if timexString.lower().find('one ') != -1 or timexString.lower().find('next ') != -1:
        distance = '1'
    elif timexString.lower().find('two ') != -1:
        distance = '2'
    elif timexString.lower().find('three ') != -1:
        distance = '3'
    elif timexString.lower().find('four ') != -1:
        distance = '4'
    elif timexString.lower().find('five ') != -1:
        distance = '5'
    elif timexString.lower().find('six ') != -1:
        distance = '6'
    elif timexString.lower().find('seven ') != -1:
        distance = '7'
    elif timexString.lower().find('eight ') != -1:
        distance = '8'
    elif timexString.lower().find('nine ') != -1:
        distance = '9'
    elif timexString.lower().find('ten ') != -1:
        distance = '10'
    elif timexString.lower().find('last ') != -1 or timexString.lower().find('earlier') != -1:
        distance = -1
    else:
        distance = 'X'
    
    if timexString.lower().find('few ') != -1:
        distance = -1
    
    if distance and distance != 'X' and int(distance) > 0 and (timexString.lower().find('earlier') > -1 or timexString.lower().find('ago') > -1):
        distance = str(-int(distance))
    
    period = ''
    if not timexValueComplete:
        if timexString.lower().find('year') != -1:
            period = 'Y'
        elif timexString.lower().find('quarter') != -1:
            period = 'Q'
        elif timexString.lower().find('month') != -1:
            period = 'M'
        elif timexString.lower().find('week') != -1:
            period = 'W'
        elif timexString.lower().find('day') != -1:
            period = 'D'
        elif timexString.lower().find('hour') != -1:
            period = 'H'
        else:
            period = 'X'

    m = numbersRx.match(timexString)
    if m:
        distance = m.group()[:-1]

    if distance == -1 and timexType == 'DURATION':
        if timexString[-1:] == 's':
            distance = 'X'
        else:
            distance = '1'

    if timexType == 'DATE':
        timexDate = dcts[t['doc']]
        
        if timexString[0:3].lower() in months:
            
            if timexString == 'may': # if not capitalised, ignore it
                continue
            
            timexMonth = timexString[0:3].lower();
            if timexString.find(' ') != -1:
                _x,  dayNumber = timexString.split(' ')
                timexDate = timexDate.replace(month=(months.index(timexMonth)+1))
                timexDate = timexDate.replace(day=int(dayNumber))
            else:
                period = 'M'
            
            daysInFuture = (timexDate - dcts[t['doc']]).days
            if daysInFuture > futureLimit:
                timexDate = timexDate.replace(year = timexDate.year - 1)

        elif distance and distance != 'X':
            distance = int(distance)
            if period == 'Y':
                timexDate += timedelta(days = 365*distance)
            elif period == 'Q':
                timexDate += timedelta(days = 90*distance)
            elif period == 'M':
                timexDate += timedelta(days = 30*distance)
            elif period == 'W':
                timexDate += timedelta(weeks = 1*distance)
            elif period == 'D':
                timexDate += timedelta(days = 1*distance)
            elif period == 'H':
                timexDate += timedelta(hours = 1*distance)
    
    
    # add one entry per attribute    
    if timexType:
        t['attr'] = 'type'
        t['value'] = timexType
        attrs.append(t.copy())
    
    if timexValue:
        
        if timexType == 'DURATION':
            timexValue = 'P' + distance + period
        elif timexType == 'DATE':
            if period == 'Y':
                timexValue = timexDate.year
            elif period in ['Q',  'M']:
                timexValue = '-'.join(map(str, [timexDate.year, '%02d' % (timexDate.month)]))
            else:
                timexValue = timexDate
        
        t['attr'] = 'value'
        t['value'] = str(timexValue)
        attrs.append(t.copy())

    print timexString,  timexType,  timexValue
    

attribsOut= open(attribsFile,  'w')
for attr in attrs:
    attribsOut.write('\t'.join([attr['doc'],  str(attr['sentence']),  str(attr['start']),  'timex3',  't'+str(attr['tid']), '1',  attr['attr'],  attr['value']]) + '\n')
attribsOut.close()

