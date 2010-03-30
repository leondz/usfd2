import re
from datetime import date,  timedelta

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
 

def addBoundary(string):
    return '^' + string + '$'

#(minute|hour|day|week|month|quarter|year) - calendar_interval
#((mon|tues|wednes|thurs|fri|satur|sun|to|yester)day|(mon|tue|wed|thu|fri|sat|sun)|tomorrow) - dayspec
#(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|[01][0-9]|`fullmonth`) - monthspec
#(january|february|march|april|may|june|july|august|september|october|november|december) - fullmonth
#19[0-9]{2}|20[00-10] - fullyear
#"[0-9]{2} - shortyear
#(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) - simple_ordinals
#((twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)?-?(one|two|three|four|five|six|seven|eight|nine)?|(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)) - textual number

#(early|late|earlier|later)? (this|next|last) (year|month|week)
#now
#(first|second|third|fourth|final) quarter
#`dayspec`? [0-9]{1-2}[./- ]`monthspec`[./- ](19|20)?[0-9]{2}
#`textual number` `calendar_interval`s?
#(recent|previous|past|first|last)? ([0-9]+|`textual number`|couple of|few)?[ -]`calendar_interval`s? (ago|later|earlier)?
#the `calendar_interval`s?
#(early|mid|end)[- ](`fullmonth`|`calendar_interval`)
#(the )?`simple_ordinals` `calendar_interval`
#(a|`textual number`) `calendar_interval`s? (earlier|later|previous|ago|since)
#`monthspec`.? `shortyear`

segmentationFile = '/home/leon/time/tempeval2/test/english/relations/base-segmentation.tab'
dctFile = '/home/leon/time/tempeval2/test/english/entities/dcts-test-en.tab'
extentsFile = 'usfd2-timex-extents'
attribsFile = 'usfd2-timex-attribs'

futureLimit = 14

months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

calendar_interval = "(minute|hour|day|weekend|week|month|quarter|year)"
longdays = "((mon|tues|wednes|thurs|fri|satur|sun|to|yester)day|tomorrow)"
dayspec = "("+longdays+"|(mon|tue|wed|thu|fri|sat|sun))"
fullmonth = "(january|february|march|april|may|june|july|august|september|october|november|december)"
monthspec = "(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"+fullmonth+")"
fullyear = "1[8-9][0-9]{2}|20[00-10]"
shortyear = "'?[0-9]{2}"
simple_ordinals = "(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"
teen = "(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)"
digits = "(one|two|three|four|five|six|seven|eight|nine)"
textual_number = "(((twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[\ \-])?"+digits+"|"+digits+"|a|an|"+teen+")"
vague = "(around|about|roughly|nearly|over)"
times = "([012][0-9][\:\.][0-5][0-9](pm|am)?|noon|breakfast|sunrise|sundown|sunset|nightfall|dawn|dusk)"

timex_re = []
timex_re.append(fullmonth)
timex_re.append(longdays)
timex_re.append("(((early|late|earlier|later) )?((this|next|last) )?("+calendar_interval+"|"+longdays+"))")
timex_re.append("(now)")
timex_re.append("((first|second|third|fourth|final) quarter)")
timex_re.append("(("+dayspec+" )?[0-9]{1,2}([\.\/\-\ ])([0-9]{1,2}|" + monthspec + ")\\7(19|20)?[0-9]{2})") # backreference id may change, be sure it's correct after altering this regex
timex_re.append("("+textual_number + "[\-\ ]" + calendar_interval + "([\-\ ](long|old))?)")
timex_re.append("(((recent|previous|past|first|last) )?(([0-9]+|"+textual_number+"|couple of|few) )?"+calendar_interval+"s?( (ago|later|earlier))?)")
timex_re.append("(the "+calendar_interval+"s?)")
timex_re.append("((early|mid|end)[\-\ ]("+fullmonth+"|"+calendar_interval+"))")
timex_re.append("((the )?"+simple_ordinals+" "+calendar_interval+")")
timex_re.append("((a|"+textual_number+") "+calendar_interval+"s? (or so )(earlier|later|previous|ago|since))")
timex_re.append("("+monthspec+"\.? "+shortyear+")")
timex_re.append("((the )(end|start|beginning|middle) of the "+calendar_interval+")")
timex_re.append("(("+longdays+"|this) (morning|afternoon|evening|night)|tonight)")
timex_re.append("((within|in ((more|less) than )("+vague+" )?)"+textual_number+" "+calendar_interval+")")
timex_re.append("((next|previous|last|following) (few|many|"+textual_number+") "+calendar_interval+"s?)")
timex_re.append("("+vague+" "+textual_number+" "+calendar_interval+")")
timex_re.append("(("+times+"( "+longdays+")?)|("+longdays+" "+times+"))")
timex_re.append("("+monthspec+"\.? [0-3]?[0-9](st|nd|rd|th)?)")


timex_re = map(addBoundary, timex_re)
#timex_re = map(re.compile, timex_re)

file = open(segmentationFile)

current_file = ''

words = {}

for line in file:
    filename,  sentence,  word,  token = line.strip().split('\t')
    sentence,  word = map(int,  [sentence,  word])
    
    if filename != current_file:
        words[filename] = []
        current_file = filename
    
    if word == 0:
        words[filename].insert(sentence,  [])
    
    words[filename][sentence].insert(word,  token)

file.close()

# ngrams[0] is empty; ngrams[1] contains unigrams; ngrams [2] bigrams, and so on.
ngrams = []
ngrams.insert(0,  [])

for n in range(1, 6):
    ngrams.insert(n,  {})
    
    for docName in words.keys():
        for sentenceIndex,  wordList in enumerate(words[docName]):
            for wordIndex,  word in enumerate(words[docName][sentenceIndex][0:-(n - 1)]):
                ngrams[n][':'.join([docName,  str(sentenceIndex),  str(wordIndex)])] = words[docName][sentenceIndex][wordIndex:wordIndex + n]

timexes = []

# feed this regex list a set of ngrams; look for complete matches.
tid = 0
for n in range(1, 6):
    for key,  wordList in ngrams[n].items():
        
        window_string = ' '.join(wordList)
        
        for test in timex_re:
            matches = re.compile(test,  re.I).finditer(window_string)

            for match in matches:
                matchDoc,  matchSentence,  matchStart = key.split(':')
                matchSentence,  matchStart = map(int,  [matchSentence,  matchStart])
                matchEnd = matchStart + n - 1
                
                c = {'doc':matchDoc,  'sentence':matchSentence,  'start':matchStart,  'end':matchEnd}
                # overlap conditions:
                # listitem, candidate. we can have: candidate early_overlap, candidate includes, candidate is_included, candidate late_overlap
                # detection for these:
                #  candidate early_overlap: c.start < l.start, c.end > l.start, c.end < l.end
                #  candidate includes: c.start < l.start, c.end > l.end
                #  candidate is_included: c.start > l.start, c.end < l.end
                #  candidate late_overlap: c.start > l.start, c.start < l.end, c.end > l.end
                #  candidate begins: c.end < 
                #  candidate ends:
                #  candidate extends:
                #  candidate precedes
                # basically, we want to know if our candidate timex has any points within the bounds of anything in the list. If so, we will extend the list item's boundaries.
                # names of conditions:
                #  candidate start early; candidate start late; candidate end early; candidate end late; candidate end during; candidate start during
                
                # list item l
                added = False
                for k, l in enumerate(timexes):
                    
                    if c['sentence'] != l['sentence'] or c['doc'] != l['doc']:
                        continue
                    
                    if c['start'] == l['start'] and c['end'] == l['end']:
                        added = True
                        break
                        
                    elif (c['start'] >= l['start'] and c['start'] <= l['end']) or (c['end'] >= l['start'] and c['end'] <= l['end']):
                        new_start = min(c['start'],  l['start'])
                        new_end = max(c['end'],  l['end'])
                        new_string = words[c['doc']][c['sentence']][new_start:new_end]
                        new_entry = {'doc':c['doc'], 'sentence':c['sentence'],  'start':new_start,  'end':new_end,  'tid':tid}
                        tid += 1
#                        print 'Merged with', l['start'], '-', l['end'], 'to',  new_entry
                        timexes[k] = new_entry
                        added = True
                        break
                
                    k += 1
                    
                if not added:
                    c['tid'] = tid
                    tid += 1
                    timexes.append(c)


print "Results:"
for t in timexes:
#    print '(%s-%s) "%s"' % (doc_timex['start'],  doc_timex['end'],  doc_timex['text'])
    timexString = ' '.join(words[t['doc']][t['sentence']][t['start']:t['end']+1])
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
durationRx = re.compile(r'\b(for|during)\b',  re.I)
numbersRx = re.compile(r'^[0-9]+ ')

for t in timexes:
    timexString = ' '.join(words[t['doc']][t['sentence']][t['start']:t['end']+1])
    
    timexType = ''
    previous3Words = ' '.join(words[t['doc']][t['sentence']][t['start']-3:t['start']-1])

    # e.g. "for 6 months" - duration
    # a year ago - date
    # a year - duration
    if durationRx.search(previous3Words) or timexString[-1:] == 's' or (timexString[0:2].lower() == 'a ' and timexString.count(' ') < 2): 
        timexType = 'DURATION'
    else:
        timexType = 'DATE'
    
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
            timexMonth = timexString[0:3].lower();
            _x,  dayNumber = timexString.split(' ')
            timexDate = timexDate.replace(month=(months.index(timexMonth)+1))
            timexDate = timexDate.replace(day=int(dayNumber))
            
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
