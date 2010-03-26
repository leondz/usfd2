import re

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
timex_re.append("("+textual_number + "[\-\ ]" + calendar_interval + "([\-\ ]long)?)")
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

#timex_re = map(re.compile, timex_re)

file = open('train_6')
input_doc = file.read().replace('\n',  ' ')

# timex list structure is, list of timex, timex is dict of start, end, text
doc_timexes= []


# feed this regex list a set of ngrams; look for complete matches.
for test in timex_re:
    matches = re.compile(test,  re.I).finditer(input_doc)

    for match in matches:
        print 'Found', match.span(),  match.group()
        # candidate timex c
        c = {'start':match.start(),  'end':match.end(),  'text':match.group()}

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
        k = 0
        for l in doc_timexes:
            if c['start'] == l['start'] and c['end'] == l['end']:
                print 'Already recognised'
                added = True
                break
                
            elif (c['start'] >= l['start'] and c['start'] <= l['end']) or (c['end'] >= l['start'] and c['end'] <= l['end']):
                new_start = min(c['start'],  l['start'])
                new_end = max(c['end'],  l['end'])
                new_string = input_doc[new_start:new_end]
                new_entry = {'start':new_start,  'end':new_end,  'text':new_string}
                print 'Merged with', l['start'], '-', l['end'], l['text'],  'to',  new_entry
                doc_timexes[k] = new_entry
                added = True
                break
              
            k += 1   
            
        if not added:
            doc_timexes.append(c)

print "Results:"
for doc_timex in doc_timexes:
    print '(%s-%s) "%s"' % (doc_timex['start'],  doc_timex['end'],  doc_timex['text'])
    
dct = '19900816'
