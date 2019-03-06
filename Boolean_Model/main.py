import re, os, glob, json, itertools
from nltk.stem import WordNetLemmatizer

_STOP_WORDS = ['a','about','above','after','again','against','all','am','an','and','any','are','aren\'t','as','at','be','because','been','before','being','below','between','both','but','by','can\'t','cannot','could','couldn\'t','did','didn\'t','do','does','doesn\'t','doing','don\'t','down','during','each','few','for','from','further','had','hadn\'t','has','hasn\'t','have','haven\'t','having','he','he\'d','he\'ll','he\'s','her','here','here\'s','hers','herself','him','himself','his','how','how\'s','i','i\'d','i\'ll','i\'m','i\'ve','if','in','into','is','isn\'t','it','it\'s','its','itself','let\'s','me','more','most','mustn\'t','my','myself','no','nor','not','of','off','on','once','only','or','other','ought','our','ours']

def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '',text.strip())               # removing punctuation
    result = re.sub(r'\d+','', text)                        #removing numbers
    return result.split(' ')
def preprocess(words):
    # print('\npreprocess')
    lem=WordNetLemmatizer()
    words = [i for i in words if not i in _STOP_WORDS]     #remove stopwords
    return list(set([lem.lemmatize(i) for i in words]))
def inverted_indexer(inverted, text, docID):
    words = preprocess(tokenize(text))
    # print('\nindexer')
    for idx,word in enumerate(words):
        does_it_exist = inverted.setdefault(word,None)   
        if does_it_exist == None:                        #if word does not exist, add word docID and index
            inverted[word] = {docID:[idx]}
        elif docID not in inverted[word].keys():         # if word exists, but docID does not add docID and index
            inverted[word][str(docID)] = [idx]
        else:                                            # if word and docID exist but index does not
            inverted[word][str(docID)].append(idx)            
            inverted[word][str(docID)] = list(set(sorted(inverted[word][str(docID)])))
    return inverted
def biword_indexer(inverted, text, docID):
    words = preprocess(tokenize(text))
    for first, second in itertools.zip_longest(words, words[1:]):
        if second is None:
            biword= first
        else:
            biword = first + " " + second
        idx = words.index(first)
        does_it_exist = inverted.setdefault(biword,None)
        if does_it_exist == None:
            inverted[biword] = {docID:[idx]}
        elif docID not in inverted[biword].keys():
            inverted[biword][docID] = [idx]
        else:
            inverted[biword][docID].append(idx)                    #adding latest docID when it does not exist
            inverted[biword][docID] = list(set(sorted(inverted[biword][docID])))
    return inverted
def save_inverted(inverted):
    with open('boolean.json', 'w') as outfile:
        json.dump(inverted, outfile)
def read_inverted():
    with open('boolean.json') as f:
        return json.load(f)
def And(l1, l2):

    l1set = set(l1.keys())
    l2set = set(l2.keys())
    if (l1set & l2set): 
        return list(l1set & l2set)
    else: 
        return "No common document"
def Or(l1,l2):
    return list(set(list(l1.keys())+list(l2.keys())))
def Not(l1, docIDS):
    return [i for i in docIDS if i not in l1.keys()]
def search(inverted,query):
    # simplify query first
    # return inverted[query] if query in inverted.keys() else None
    query = query.split(" ")
    docIDS = inverted["docIDS"]
    if len(query)==1:
        print(inverted[query[0]] if query[0] in inverted.keys() else None)
    elif len(query)==2:
        if query[0] == "not":
            print("->")
            print(Not(inverted[query[1]] if query[1] in inverted.keys() else None, docIDS))
        else:
            biword = query[0] + " " + query[1]
            print("->")
            print(inverted[biword] if biword in inverted.keys() else None)
    elif len(query)==3:
        l1 = inverted[query[0]] if query[0] in inverted.keys() else None
        l2 = inverted[query[2]] if query[2] in inverted.keys() else None
        if query[1] not in ["and","or"]:
            proximity = int(query[1][-1])
            # print(proximity)
            common = And(l1,l2)
            # print(common)
            result = []
            for docID in common:
                # print(docID)
                one = inverted[query[0]][docID]
                two = inverted[query[2]][docID]
                for i in one:
                    # print(i)
                    for j in two:
                        # print(j)
                        # print(abs(i-j))
                        # print(proximity)
                        if abs(i-j) == proximity:
                            # print('if')
                            # print(abs(i-j))
                            # print(proximity)
                            result.append(docID)
            print("->")
            print(result)        

        elif query[1]=="and":
            if l1 is None or l2 is None:
                print('Either of the two search query words does not exist in the inverted index\n')
            else:
                print("->")
                print(And(l1,l2))
        elif query[1]=="or":
            if l1 is None and l2 is None:
                print('Either of the two search query words does not exist in the inverted index\n')
            elif l1 is None:
                print(query[0] + ' does not exist in inverted index.\nReturning posting list for the other word\n')
                print("->")
                print(inverted[query[2]])
            elif l2 is None:
                print(query[2] + ' does not exist in inverted index.\nReturning posting list for the other word\n')
                print("->")
                print(inverted[query[0]])
            else:
                print("->")
                print(Or(l1,l2))
        # else:
    elif len(query)==4:
        if query[1] not in ["and", "or"] and query[2] not in ["and", "or"]: # proximity for biword
            if "/" in query[1]:
                biword = query[2] + " " + query[3]
                l1 = inverted[query[0]] if query[0] in inverted.keys() else None
                l2 = inverted[biword] if biword in inverted.keys() else None
                proximity = int(query[1][-1])
                common = And(l1,l2)
                result = []
                for docID in common:
                    one = inverted[query[0]][docID]
                    two = inverted[biword][docID]
                    for i in one:
                        for j in two:
                            if abs(i-j) == proximity:
                                result.append(docID)
                print("->")
                print(result)
            elif "/" in query[2]:
                biword = query[0] + " " + query[1]
                l1 = inverted[biword] if biword in inverted.keys() else None
                l2 = inverted[query[3]] if query[3] in inverted.keys() else None
                proximity = int(query[2][-1])
                common = And(l1,l2)
                result = []
                for docID in common:
                    one = inverted[biword][docID]
                    two = inverted[query[3]][docID]
                    for i in one:
                        for j in two:
                            if abs(i-j) == proximity:
                                result.append(docID)
                print("->")
                print(result)
        elif query[1]!="not" and query[2]=="and":                           #biword and word
            biword = query[0] + " " + query[1]
            l2 = inverted[query[3]] if query[3] in inverted.keys() else None
            l1 = inverted[biword] if biword in inverted.keys() else None
            if l1 is None or l2 is None:
                print('Either of the two search query words does not exist in the inverted index\n')
            else:
                print("->")
                print(And(l1,l2))
        elif query[1]!="not" and query[2]=="or":                            #biword or word
            biword = query[0] + " " + query[1]
            l2 = inverted[query[3]] if query[3] in inverted.keys() else None
            l1 = inverted[biword] if biword in inverted.keys() else None
            if l1 is None and l2 is None:
                print('Either of the two search query words does not exist in the inverted index\n')
            elif l1 is None:
                print(biword + ' does not exist in inverted index.\nReturning posting list for the other word\n')
                print("->")
                print(inverted[query[3]])
            elif l2 is None:
                print(query[3] + ' does not exist in inverted index.\nReturning posting list for the other word\n')
                print("->")
                print(inverted[biword])
            else:
                print("->")
                print(Or(l1,l2))
        elif query[1]=="and" and query[2]!="not":                           #word and biword
            biword = query[2] + " " + query[3]
            l1 = inverted[query[0]] if query[0] in inverted.keys() else None
            l2 = inverted[biword] if biword in inverted.keys() else None
            if l1 is None or l2 is None:
                print('Either of the two search query words does not exist in the inverted index\n')
            else:
                print("->")
                print(And(l1,l2))
        elif query[1] == "and" and query[2] == "not":                       # word and not word
            l1 = inverted[query[0]] if query[0] in inverted.keys() else None
            l2 = inverted[query[3]] if query[3] in inverted.keys() else None
            print("->")
            print(And(l1,Not(l2,docIDS)))
        elif query[1]=="or" and query[2]!="not":                            # word or biword
            biword = query[2] + " " + query[3]
            l1 = inverted[query[0]] if query[0] in inverted.keys() else None
            l2 = inverted[biword] if biword in inverted.keys() else None
            if l1 is None and l2 is None:
                print('Either of the two search query words does not exist in the inverted index\n')
            elif l1 is None:
                print(query[0] + ' does not exist in inverted index.\nReturning posting list for the other word\n')
                print("->")
                print(inverted[biword])
            elif l2 is None:
                print(biword + ' does not exist in inverted index.\nReturning posting list for the other word\n')
                print("->")
                print(inverted[query[0]])
            else:
                print("->")
                print(Or(l1,l2))
        elif query[1] == "or" and query[2] == "not":                        # word or not word
            l1 = inverted[query[0]] if query[0] in inverted.keys() else None
            l2 = inverted[query[3]] if query[3] in inverted.keys() else None
            print("->")
            print(Or(l1,Not(l2,docIDS)))    
        elif query[0] == "not" and query[2] == "and":                       # not word and word
            l1 = inverted[query[1]] if query[1] in inverted.keys() else None
            l2 = inverted[query[3]] if query[3] in inverted.keys() else None
            print("->")
            print(And(l2,Not(l1,docIDS)))
        elif query[0] == "not" and query[2] == "or":                        # not word or word
            l1 = inverted[query[1]] if query[1] in inverted.keys() else None
            l2 = inverted[query[3]] if query[3] in inverted.keys() else None
            print("->")
            print(Or(l2,Not(l1,docIDS)))
    elif len(query)==5:
        if '/' in query[2]:
            biword1 = query[0] + " " + query[1]
            biword2 = query[3] + " " + query[4]
            l1 = inverted[biword1] if biword1 in inverted.keys() else None
            l2 = inverted[biword2] if biword2 in inverted.keys() else None
            proximity = int(query[2][-1])
            common = And(l1,l2)
            result = []
            for docID in common:
                one = inverted[biword1][docID]
                two = inverted[biword2][docID]
                for i in one:
                    for j in two:
                        if abs(i-j) == proximity:
                            result.append(docID)
            
            print("->")
            print(result)

def main():
    inverted = read_inverted()
    path = os.getcwd()
    counter = 1
    inverted["docIDS"] = []
    for filename in glob.glob(os.path.join(path, '*.txt')):
        f = open(filename, 'r')
        content = f.read()
        content = re.sub('\n',' ',content)
        content = re.sub('\t',' ',content)
        inverted = inverted_indexer(inverted,content,counter)
        inverted = biword_indexer(inverted,content, counter)
        inverted["docIDS"].append(counter)
        inverted["docIDS"] = list(set(inverted["docIDS"]))
        save_inverted(inverted)
        counter +=1
    print("Success. Check boolean.json\n")
    while(True):
        query = str(input("Enter search query. Use lowercase logical operator. Ex. and, or, not. Enter 0 to quit.\n"))
        if query == "0":
            break
        else:
            search(inverted,query)


if __name__=='__main__':
        main()
