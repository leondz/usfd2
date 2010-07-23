import re


def addBoundary(string):
    return '^' + string + '$'
    
    
def buildSentenceList(sentenceDict): # convert a sentence dictionary including character offsets to an ordered and tokenised sentence list
    # sort by key, then return items in order.
    items = sentenceDict.items()
    items.sort()
    sentenceList = []
    for position,  word in items:
        sentenceList.insert(position, word)
    return sentenceList


#DETECTION RULES:
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


def findTimexes(words):  # expects words to be in the format words[filename][sentence index][word index] = "token" .
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    calendar_interval = "(minute|hour|day|weekend|week|month|quarter|year)"
    longdays = "((mon|tues|wednes|thurs|fri|satur|sun|to|yester)day|tomorrow)"
    dayspec = "("+longdays+"|(mon|tue|wed|thu|fri|sat|sun))"
    fullmonth = "(january|february|march|april|may|june|july|august|september|october|november|december)"
    monthspec = "(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"+fullmonth+")"
    fullyear = "1[8-9][0-9]{2}|20[00-10]"
    shortyear = "'?[0-9]{2}"
    simple_ordinals = "(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"
    numeric_days = "([0-9]{1,2}(st|nd|rd|th)?)"
    teen = "(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)"
    digits = "(one|two|three|four|five|six|seven|eight|nine)"
    textual_number = "(((twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[\ \-])?"+digits+"|"+digits+"|a|an|"+teen+")"
    vague = "(around|about|roughly|nearly|over)"
    times = "([012][0-9][\:\.][0-5][0-9](pm|am)?|noon|breakfast|sunrise|sundown|sunset|nightfall|dawn|dusk)"
    year = '('+fullyear+'|'+shortyear+')'

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
    timex_re.append("("+monthspec+"\.? "+year+")")
    timex_re.append("((the )(end|start|beginning|middle) of the "+calendar_interval+")")
    timex_re.append("(("+longdays+"|this) (morning|afternoon|evening|night)|tonight)")
    timex_re.append("((within|in ((more|less) than )("+vague+" )?)"+textual_number+" "+calendar_interval+")")
    timex_re.append("((next|previous|last|following) (few|many|"+textual_number+") "+calendar_interval+"s?)")
    timex_re.append("("+vague+" "+textual_number+" "+calendar_interval+")")
    timex_re.append("(("+times+"( "+longdays+")?)|("+longdays+" "+times+"))")
    timex_re.append("("+monthspec+"\.? [0-3]?[0-9](st|nd|rd|th)?)")
    timex_re.append("("+numeric_days+"? "+monthspec+" "+year+"?)")


    timex_re = map(addBoundary, timex_re)

    # ngrams[0] is empty; ngrams[1] contains unigrams; ngrams [2] bigrams, and so on.
    ngrams = []
    ngrams.insert(0,  [])

    # build ngrams of input string
    for n in range(1, 6):
        ngrams.insert(n,  {})
        
        for docName in words.keys():
            for sentenceIndex,  wordList in enumerate(words[docName]):
                sentenceList = buildSentenceList(words[docName][sentenceIndex])
                
                if n == 1:
                    maxBound = len(sentenceList)
                else:
                    maxBound = -(n - 1)
                    
                for wordIndex,  word in enumerate(sentenceList[0:maxBound]):
                    ngrams[n][':'.join([docName,  str(sentenceIndex),  str(wordIndex)])] = sentenceList[wordIndex:wordIndex + n]

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
                            expanded_start = min(c['start'],  l['start'])
                            expanded_end = max(c['end'],  l['end'])
                            expanded_string = buildSentenceList(words[c['doc']][c['sentence']])[expanded_start:expanded_end]
                            expanded_entry = {'doc':c['doc'], 'sentence':c['sentence'],  'start':expanded_start,  'end':expanded_end,  'tid':tid}
                            tid += 1
    #                        print 'Merged with', l['start'], '-', l['end'], 'to',  expanded_entry
                            timexes[k] = expanded_entry
                            added = True
                            break
                    
                        k += 1
                        
                    if not added:
                        c['tid'] = tid
                        tid += 1
                        timexes.append(c)

    return timexes
    
def getTimexType(timexString,  previous3Words):

    durationRx = re.compile(r'\b(for|during)\b',  re.I)

    # e.g. "for 6 months" - duration
    # a year ago - date
    # a year - duration
    if durationRx.search(previous3Words) or timexString[-1:] == 's' or (timexString[0:2].lower() == 'a ' and timexString.count(' ') < 2): 
        timexType = 'DURATION'
    else:
        timexType = 'DATE'
    
    return timexType

def annotateTimexesKBP(inputString,  tag="timex"):
    # return a list off start/finish offset pairs; []{start_char=xx, end_char=yy}
    
    # tokenise string
    from nltk import word_tokenize
    tokens = word_tokenize(inputString)
    #tokens = inputString.split(' ')
#    print tokens
    
    
    # convert to words[file][sent][word] = "token"
    words = {}
    words['stdin'] = {}
    words['stdin'][0] = {}
    
    offset = 0
    for token in tokens:
        words['stdin'][0][offset] = token
        offset += 1
    
    # get timexes
    timexes = findTimexes(words)
    
    outputOffsets = []
    
    for t in timexes:
        timexString = ' '.join(buildSentenceList(words[t['doc']][t['sentence']])[t['start']:t['end']+1])
        
        # only annotate DATE timexes
        previous3Words = ' '.join(tokens[t['start']-3:t['start']-1])
        if getTimexType(timexString,  previous3Words) != 'DATE':
            continue
        
#        print t,  timexString
        offsets = {}
        start_char = inputString.find(timexString)
        end_char = start_char + len(timexString)
        
#        print inputString[start_char:end_char]
        offsets['start_char'] = start_char
        offsets['end_char'] = end_char
        outputOffsets.append(offsets.copy())
        
    
    return outputOffsets
