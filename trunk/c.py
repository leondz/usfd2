import tempEval2
import nltk
import nltk.classify.maxent

trainPath = '/home/leon/time/tempeval2/training2/english/data/'
testPath = '/home/leon/time/tempeval2/test/english/relations/'

trainWords = tempEval2.readSegmentation(trainPath + 'base-segmentation.tab')
trainTimexExtents = tempEval2.readExtents(trainPath + 'timex-extents.tab')
trainEventExtents = tempEval2.readExtents(trainPath + 'event-extents.tab')
trainTimexAttribs = tempEval2.readAttributes(trainPath + 'timex-attributes.tab')
trainEventAttribs = tempEval2.readAttributes(trainPath + 'event-attributes.tab')
trainTlinks = tempEval2.readRelations(trainPath + 'tlinks-timex-event.tab')

signals = tempEval2.readSignalHints('signals.tab')


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
        
        if relation['from'][0] == 'e':
            arg1 = trainEventAttribs[document][relation['from']]
        else:
            arg1 = trainTimexAttribs[document][relation['from']]

        if relation['to'][0] == 'e':
            arg2 = trainEventAttribs[document][relation['to']]
        else:
            arg2 = trainTimexAttribs[document][relation['to']]

        features['arg1word'] = arg1['startWord']
        features['arg1type'] = arg1['type']
        for k, v in arg1['a'].items():
            features['arg1'+k] = v

        features['arg2word'] = arg2['startWord']
        features['arg2type'] = arg2['type']
        for k, v in arg1['a'].items():
            features['arg2'+k] = v
        
        
        examples.append((features,  relType))


classifier = nltk.MaxentClassifier.train(examples)

die

# per sentence, look for sentences that contain both a timex and an event
#   fantastic! we will create a relation between these two.
#   look for the presence of a signal
#       do we have one? if so, look at word ordering to see if the signal need be reversed
#       add a relation and its source. maybe we can have a set of weighted probabilities for each relation? 
#       e.g. rels[doc][event-timex][{src:signal suggestions:{before:1}}, {src:maxent suggestions:{before:0.7, overlap:0.3}, {src:mcc suggestions:{before:1}}]

relations = {}

# hah!
# for each document, are there both timexs and events in this document? 
# if so, get the sentences, and check one by one if there are any timexs in the sentence
# when there are, look at the events in the document and see if there are any in this sentence
# if so, add an empty pair to relations; we have a same-sentence event-timex relation.

for document in trainWords:
    relations[document] = {}
    if document in trainTimexExtents.keys() and document in trainEventExtents.keys():
        for sentence in document:
            for timex in trainTimexExtents[document]:
                if trainTimexExtents[document][timex]['sentence'] == sentence:
                        for event in trainEventExtents[document]:
                            if trainEventExtents[document][event]['sentence'] == sentence:
                                relations[document][event + '-' + timex] = {}
    
for document,  docRelations in relations.items():
    if docRelations == {}:
        del relations[document]
        continue
    
    for relationId,  relationData in docRelations.items():
        eventId,  timexId = relationId.split('-')
        sentence = int(trainTimexExtents[document][timexId]['sentence'])
        timexStart = int(trainTimexExtents[document][timexId]['start'])
        eventStart = int(trainEventExtents[document][eventId]['start'])
        sentenceText = ' '.join(trainWords[document][sentence].values())
        print '%s: %s-%s in sentence %s; timex @ %s "%s", event @ %s "%s"' % (document,  eventId,  timexId,  sentence,  timexStart,  trainWords[document][sentence][timexStart],  eventStart,  trainWords[document][sentence][eventStart])
        
        signalHint = {}
        sentenceSignals = [] # list of word positions where signals are found
        for signal in signals:
            for position,  word in trainWords[document][sentence].items():
                if word.lower() == signal:
                    sentenceSignals.append(position)
        
        if sentenceSignals:
            print sentenceText
            for signalPosition in sentenceSignals:
                print trainWords[document][sentence][signalPosition],  '@',  signalPosition
        
        if len(sentenceSignals) > 1:
            #pick signal closest to event/timex midpoint
            pass
        
    
