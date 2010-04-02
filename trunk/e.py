import tempEval2
import nltk
import nltk.classify.maxent

trainPath = '/home/leon/time/tempeval2/training2/english/data/'
#testPath = '/home/leon/time/tempeval2/training2/english/data/'
testPath = '/home/leon/time/tempeval2/test/english/relations/'

linksFile = 'tlinks-main-events.tab'

trainWords = tempEval2.readSegmentation(trainPath + 'base-segmentation.tab')
trainTimexExtents = tempEval2.readExtents(trainPath + 'timex-extents.tab')
trainEventExtents = tempEval2.readExtents(trainPath + 'event-extents.tab')
trainTimexAttribs = tempEval2.readAttributes(trainPath + 'timex-attributes.tab')
trainEventAttribs = tempEval2.readAttributes(trainPath + 'event-attributes.tab')
trainTlinks = tempEval2.readRelations(trainPath + linksFile)

signals = tempEval2.readSignalHints('signals.tab')

testWords = tempEval2.readSegmentation(testPath + 'base-segmentation.tab')
testTimexExtents = tempEval2.readExtents(testPath + 'timex-extents.tab')
testEventExtents = tempEval2.readExtents(testPath + 'event-extents.tab')
testTimexAttribs = tempEval2.readAttributes(testPath + 'timex-attributes.tab')
testEventAttribs = tempEval2.readAttributes(testPath + 'event-attributes.tab')



# get most-common-relation in training data
classDistr = {}
links = 0
for docName in trainTlinks:
    for link in trainTlinks[docName]:
        links += 1
        relType = link['relType'] 
        if relType in classDistr.keys():
            classDistr[relType] += 1
        else:
            classDistr[relType] = 1

for k, v in classDistr.items():
    classDistr[k] = float(v) / float(links)




# build training examples; these look like (dict_of_features_and_values{}, class)
examples = []
for document in trainTlinks:
    for relation in trainTlinks[document]:
        features = {}
        print relation
        
        relType = relation['relType']
        
        arg1id,  arg2id = relation['from'],  relation['to']
        
        if relation['from'][0] == 'e':
            arg1 = trainEventAttribs[document][relation['from']]
            arg1sentence = int(trainEventExtents[document][arg1id]['sentence'])
        else:
            arg1 = trainTimexAttribs[document][relation['from']]
            arg1sentence = int(trainTimexExtents[document][arg1id]['sentence'])

        if relation['to'][0] == 'e':
            arg2 = trainEventAttribs[document][relation['to']]
            arg2sentence = int(trainEventExtents[document][arg2id]['sentence'])
        else:
            arg2 = trainTimexAttribs[document][relation['to']]
            arg2sentence = int(trainTimexExtents[document][arg2id]['sentence'])



        features['arg1by5'] = (int(arg1['startWord']) + 4) / 5
        features['arg1intervalType'] = arg1['type']
        for k, v in arg1['a'].items():
            features['arg1'+k] = v

        features['arg2by5'] = (int(arg2['startWord']) + 4) / 5
        features['arg2intervalType'] = arg2['type']
        for k, v in arg1['a'].items():
            features['arg2'+k] = v
        
        features['arg1word'] = trainWords[document][int(arg1['sentence'])][int(arg1['startWord'])]
        features['arg2word'] = trainWords[document][int(arg2['sentence'])][int(arg2['startWord'])]
        # include associated signal - so we need to do signal scanning + assoc for this sentence
        
        if relation['to'][0] == 'e' and relation['from'][0] == 'e':
            try:
                if arg1['a']['TENSE'] == arg2['a']['TENSE']:
                    features['sameTense'] == True
                else:
                    features['sameTense'] == False
            except Exception:
                pass
            
            try:
                if arg1['a']['ASPECT'] == arg2['a']['ASPECT']:
                    features['sameAspect'] == True
                else:
                    features['sameAspect'] == False
            except Exception:
                pass
        
        
        if arg2sentence < arg1sentence:
            features['e1e2'] = False
        elif arg1sentence == arg2sentence and arg2['startWord'] < arg1['startWord']:
            features['e1e2'] = False
        else:
            features['e1e2'] = True
        
        
        signalHint1 = 'none'
        # this will hold two values; [distance_from_arg, absolute_offset]
        nearestSignal1 = [9999, -1]
        signalHint2 = 'none'
        nearestSignal2 = [9999,  -1]
        
        arg1sentenceText = ' '.join(trainWords[document][arg1sentence].values())
        arg2sentenceText = ' '.join(trainWords[document][arg1sentence].values())
        
        for signal,  _x in signals.items():
            signalPos1 = arg1sentenceText.lower().find(signal)
            signalPos2 = arg2sentenceText.lower().find(signal)
            
            if signalPos1 != -1:
                sigDist = abs(signalPos1 - int(arg1['startWord']))
                if sigDist < nearestSignal1[0]:
                    nearestSignal = [sigDist,  signalPos1]
            
            if signalPos2 != -1:
                sigDist = abs(signalPos2 - int(arg2['startWord']))
                if sigDist < nearestSignal2[0]:
                    nearestSignal = [sigDist,  signalPos2]
        
        if nearestSignal1[1] != -1:
            signalHint1 = signals[trainWords[document][arg1sentence][nearestSignal1[1]]]
            features['arg1signal'] = nearestSignal1[1] - arg1['startWord']
        
        if nearestSignal2[1] != -1:
            signalHint2 = signals[trainWords[document][arg2sentence][nearestSignal2[1]]]
            features['signalarg2'] = arg2['startWord'] - nearestSignal2[1]
        
        features['signalHint1'] = signalHint1
        features['signalHint2'] = signalHint2
        
        examples.append((features,  relType))


classifier = nltk.MaxentClassifier.train(examples)


# per sentence, look for sentences that contain both a timex and an event
#   fantastic! we will create a relation between these two.
#   look for the presence of a signal
#       do we have one? if so, look at word ordering to see if the signal need be reversed
#       add a relation and its source. maybe we can have a set of weighted probabilities for each relation? 
#       e.g. rels[doc][event-timex][{src:signal suggestions:{before:1}}, {src:maxent suggestions:{before:0.7, overlap:0.3}, {src:mcc suggestions:{before:1}}]


# read relations in from test links file



outfile = open(linksFile,  'w')

inLinksFile = open(testPath + linksFile)
current_file = ''

for line in inLinksFile:
    document, arg1id,  arg2id,  _x = line.strip().split('\t')
    
    if document != current_file:
        current_file = document

        
    if arg1id[0] == 'e':
        arg1 = testEventAttribs[document][arg1id]
        arg1sentence = int(testEventExtents[document][arg1id]['sentence'])
    elif arg1id[0] == 't':
        arg1 = testTimexAttribs[document][arg1id]
        arg1sentence = int(testTimexExtents[document][arg1id]['sentence'])
    else:
        die

    if arg2id[0] == 'e':
        arg2 = testEventAttribs[document][arg2id]
        arg2sentence = int(testEventExtents[document][arg2id]['sentence'])
    elif arg2id[0] == 't':
        arg2 = testTimexAttribs[document][arg2id]
        arg2sentence = int(testTimexExtents[document][arg2id]['sentence'])
    else:
        die
    
    arg1Start = int(arg1['startWord'])
    arg2Start = int(arg2['startWord'])
    
    arg1sentenceText = ' '.join(testWords[document][arg1sentence].values())
    arg2sentenceText = ' '.join(testWords[document][arg1sentence].values())
    
    printArgs = (document,  arg1id,  arg2id,  arg1sentence,  arg2sentence,  arg1['type'],  arg1Start,  testWords[document][arg1sentence][arg1Start]
                 ,  arg2['type'], arg2Start, testWords[document][arg2sentence][arg2Start])
    print '%s: %s-%s in sentences %s,%s; arg1 (%s) @ %s "%s", arg2 (%s) @ %s "%s"' % printArgs
    
    
    # represent this pair as a feature list
    features = {}
    features['arg1by5'] = (int(arg1['startWord']) + 4) / 5
    features['arg1intervalType'] = arg1['type']
    for k, v in arg1['a'].items():
        features['arg1'+k] = v
    
    features['arg2by5'] = (int(arg2['startWord']) + 4) / 5
    features['arg2intervalType'] = arg2['type']
    for k, v in arg2['a'].items():
        features['arg2'+k] = v
    
    features['arg1word'] = testWords[document][int(arg1['sentence'])][int(arg1['startWord'])]
    features['arg2word'] = testWords[document][int(arg2['sentence'])][int(arg2['startWord'])]
    # include associated signal - so we need to do signal scanning + assoc for this sentence
    
    if relation['to'][0] == 'e' and relation['from'][0] == 'e':
        
        try:
            if arg1['a']['TENSE'] == arg2['a']['TENSE']:
                features['sameTense'] == True
            else:
                features['sameTense'] == False
        except Exception:
            pass
        
        try:
            if arg1['a']['ASPECT'] == arg2['a']['ASPECT']:
                features['sameAspect'] == True
            else:
                features['sameAspect'] == False
        except Exception:
            pass
    
    
    if arg2sentence < arg1sentence:
        features['e1e2'] = False
    elif arg1sentence == arg2sentence and arg2['startWord'] < arg1['startWord']:
        features['e1e2'] = False
    else:
        features['e1e2'] = True
    
    
    signalHint1 = 'none'
    # this will hold two values; [distance_from_arg, absolute_offset]
    nearestSignal1 = [9999, -1]
    signalHint2 = 'none'
    nearestSignal2 = [9999,  -1]
    
    arg1sentenceText = ' '.join(testWords[document][arg1sentence].values())
    arg2sentenceText = ' '.join(testWords[document][arg1sentence].values())
    
    for signal,  _x in signals.items():
        signalPos1 = arg1sentenceText.lower().find(signal)
        signalPos2 = arg2sentenceText.lower().find(signal)
        
        if signalPos1 != -1:
            sigDist = abs(signalPos1 - int(arg1['startWord']))
            if sigDist < nearestSignal1[0]:
                nearestSignal = [sigDist,  signalPos1]
        
        if signalPos2 != -1:
            sigDist = abs(signalPos2 - int(arg2['startWord']))
            if sigDist < nearestSignal2[0]:
                nearestSignal = [sigDist,  signalPos2]
    
    if nearestSignal1[1] != -1:
        signalHint1 = signals[testWords[document][arg1sentence][nearestSignal1[1]]]
        features['arg1signal'] = nearestSignal1[1] - arg1['startWord']
    
    if nearestSignal2[1] != -1:
        signalHint2 = signals[testWords[document][arg2sentence][nearestSignal2[1]]]
        features['arg2signal'] = arg2['startWord'] - nearestSignal2[1]
    
    features['signalHint1'] = signalHint1
    features['signalHint2'] = signalHint2
    
    
    
    classification = classifier.classify(features)
    
    outfile.write('\t'.join([document, arg1id,  arg2id,  classification])+'\n')


outfile.close()
inLinksFile.close()

classifier.show_most_informative_features(5)
