import re


def readSegmentation(path):
    file = open(path)

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

    return words
