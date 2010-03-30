def readSegmentation(path):
    file = open(path)

    current_file = ''

    words = {}
    # structure is words[filename][sentence][word] = token

    for line in file:
        filename,  sentence,  word,  token = line.strip().split('\t')
        sentence,  word = map(int,  [sentence,  word])
        
        if filename != current_file:
            words[filename] = {}
            current_file = filename
        
        if word == 0:
            words[filename][sentence] = {}
        
        words[filename][sentence][word] = token

    file.close()

    return words


def readExtents(path):
    
    # structure is extents[filename][id] = {start:startword, end:endword}
    extents = {}
    
    file = open(path)
    current_file = ''
    current_id = ''
    
    for line in file:
        filename,  sentence,  word,  intervalType,  id,  _x = line.strip().split('\t')
        
        if filename != current_file:
            extents[filename] = {}
            current_file = filename
        
        if id != current_id:
            extents[filename][id] = {'start':-1,  'end':-1,  'sentence':sentence}
        
        if extents[filename][id]['start'] == -1 or extents[filename][id]['start'] > word:
            extents[filename][id]['start'] = word
        
        if extents[filename][id]['end'] == -1 or extents[filename][id]['end'] < word:
            extents[filename][id]['end'] = word

    file.close()
    
    return extents


def readSignalHints(path):
    
    # structure is signals['signal text'] = 'relation'
    signals = {}
    
    file = open(path)
    
    for line in file:
        signal,  relation = line.strip().split('\t')
        signals[signal] = relation
    file.close()
    
    return signals


def readRelations(path):

    # structure is relations[filename][0..n] = {'from':arg1, 'to':arg2, 'reltype':reltype}
    relations = {}
    
    current_file =''
    
    file = open(path)
    for line in file:
        docName,  arg1,  arg2,  relType = line.strip().split('\t')
        
        if docName != current_file:
            relations[docName] = []
        
        relation = {'from':arg1,  'to':arg2,  'relType':relType}
        relations[docName].append(relation)

    return relations


def readAttributes(path):
    
    # structure is attributes[filename][id] = {'sentence':int, 'startWord':int, 'type':timex3|event, a{attribs}}
    attributes = {}
    
    current_file = {}
    current_id = None
    
    file = open(path)
    for line in file:
        if len(line.strip().split('\t')) != 8:
            print 'Faulty line: "'+line+'"'
            continue
        
        docName, sentence,  startWord,  type,  id,  _x,  attrName,  attrVal = line.strip().split('\t')
        
        if docName != current_file:
            attributes[docName] = {}
            current_file = docName
            current_id = None
        
        if id != current_id:
            attributes[docName][id] = {'sentence':sentence,  'startWord':startWord,  'type':type,  'a':{attrName:attrVal}}
            current_id = id
        else:
            attributes[docName][id]['a'][attrName] = attrVal

    file.close()
    
    return attributes
    
