from collections import defaultdict
from functools import reduce
import math
import sys

document_filenames = {0 : "./Collection/lotr.txt",
                      1 : "./Collection/silmarillion.txt",
                      2 : "./Collection/rainbows_end.txt",
                      3 : "./Collection/the_hobbit.txt",
                      4 : "./Collection/Text1.txt",
                      5 : "./Collection/Text2.txt",
                      6 : "./Collection/Text3.txt",
                      7 : "./Collection/Text4.txt",
                      8 : "./Collection/TExt5.txt"}
N = len(document_filenames)

# dictionary: a set to contain all terms (i.e., words) in the document corpus.
dictionary = set()

# postings[term] is the postings list for term, and postings[term][id] is the frequency with which term appears in document id.
postings = defaultdict(dict)
document_frequency = defaultdict(int)
length = defaultdict(float)

characters = " .,!#$%^&*();:\n\t\\\"?!{}[]<>"

def initialize_terms_and_postings():
    """Reads in each document in document_filenames, splits it into a
    list of terms (i.e., tokenizes it), adds new terms to the global
    dictionary, and adds the document to the posting list for each
    term, with value equal to the frequency of the term in the
    document."""
    global dictionary, postings
    for id in document_filenames:
        f = open(document_filenames[id],'r')
        document = f.read()
        f.close()
        terms = tokenize(document)
        unique_terms = set(terms)
        dictionary = dictionary.union(unique_terms)
        for term in unique_terms:
            postings[term][id] = terms.count(term) # the value is the frequency of the term in the document

def tokenize(document):
    # print("Tokenise")
    """Returns a list whose elements are the separate terms in
    document.  Something of a hack, but for the simple documents we're
    using, it's okay.  Note that we case-fold when we tokenize, i.e.,
    we lowercase everything."""
    terms = document.lower().split()
    return [term.strip(characters) for term in terms]

def initialize_document_frequencies():
    global document_frequency
    for term in dictionary:
        document_frequency[term] = len(postings[term])

def initialize_lengths():
    global length
    # print("Initialise lengths")
    for id in document_filenames:
        l = 0
        for term in dictionary:
            l += tfIdfScore(term,id)**2
        length[id] = math.sqrt(l)

def tfIdfScore(term,id):
    # print("tf-idf Score")
    if id in postings[term]:
        return (1 + math.log(postings[term][id],10))*inverse_document_frequency(term)
    else:
        return 0.0

def inverse_document_frequency(term):
    # print("IDF")
    if term in dictionary:
        return math.log(N/document_frequency[term],10)
    else:
        return 0.0

def do_search():
    """Asks the user what they would like to search for, and returns a
    list of relevant documents, in decreasing order of cosine
    similarity."""
    query = tokenize(input("Search query >> "))
    if query == []:
        sys.exit()
    relevant_document_ids = intersection([set(postings[term].keys()) for term in query])
    if not relevant_document_ids:
        print("No documents matched all query terms.")
    else:
        scores = sorted([(id,similarity(query,id)) for id in relevant_document_ids], key=lambda x: x[1], reverse=True)
        print("Score: filename")
        for (id,score) in scores:
            print(str(round(score,4))+": "+document_filenames[id])

def intersection(sets):
    return reduce(set.intersection, [s for s in sets])

def similarity(query,id):
    """Returns the cosine similarity between query and document id.
    Note that we don't bother dividing by the length of the query
    vector, since this doesn't make any difference to the ordering of
    search results."""
    similarity = 0.0
    # print("Similarity")
    for term in query:
        if term in dictionary:
            similarity += inverse_document_frequency(term)*tfIdfScore(term,id)
    similarity = similarity / length[id]
    return similarity

def main():
    initialize_terms_and_postings()
    initialize_document_frequencies()
    initialize_lengths()
    while True:
        do_search()

if __name__ == "__main__":
    main()